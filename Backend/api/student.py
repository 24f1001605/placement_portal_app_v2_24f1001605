from flask import Blueprint, request, jsonify, send_from_directory, make_response
from flask_security import auth_required, current_user
from models import db, PlacementDrive, Application, Student
from extensions import cache
from datetime import datetime
import os
import io
import csv

student_bp = Blueprint('student', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def student_required(f):
    from functools import wraps
    @wraps(f)
    @auth_required('token', 'session')
    def decorated(*args, **kwargs):
        if not current_user.has_role('student'):
            return jsonify({'message': 'Student access required'}), 403
        return f(*args, **kwargs)
    return decorated

@student_bp.route('/dashboard', methods=['GET'])
@student_required
def dashboard():
    s = current_user.student_profile
    apps = Application.query.filter_by(student_id=s.id).all()
    return jsonify({
        'student': {
            'id': s.id,
            'name': s.name,
            'branch': s.branch,
            'cgpa': s.cgpa,
            'year': s.year,
            'contact': s.contact,
            'skills': s.skills,
            'resume_url': s.resume_url,
            'email': current_user.email
        },
        'total_applications': len(apps),
        'shortlisted': sum(1 for a in apps if a.status == 'Shortlisted'),
        'selected': sum(1 for a in apps if a.status == 'Selected')
    }), 200

@student_bp.route('/profile', methods=['PUT'])
@student_required
def update_profile():
    s = current_user.student_profile
    data = request.get_json()
    s.name = data.get('name', s.name)
    s.branch = data.get('branch', s.branch)
    s.cgpa = float(data.get('cgpa', s.cgpa))
    s.year = int(data.get('year', s.year))
    s.contact = data.get('contact', s.contact)
    s.skills = data.get('skills', s.skills)
    s.address = data.get('address', s.address)
    db.session.commit()
    return jsonify({'message': 'Profile updated'}), 200

# --- RESUME UPLOAD ---
@student_bp.route('/resume/upload', methods=['POST'])
@student_required
def upload_resume():
    s = current_user.student_profile
    if 'resume' not in request.files:
        return jsonify({'message': 'No file uploaded'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'message': 'Only PDF, DOC, DOCX files allowed'}), 400

    if file.content_length and file.content_length > 5 * 1024 * 1024:
        return jsonify({'message': 'File size must be under 5MB'}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"resume_student_{s.id}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    s.resume_url = filename
    db.session.commit()
    return jsonify({'message': 'Resume uploaded successfully!', 'resume_url': filename}), 200

# --- RESUME DOWNLOAD ---
@student_bp.route('/resume/download/<int:sid>', methods=['GET'])
@auth_required('token', 'session')
def download_resume(sid):
    student = Student.query.get_or_404(sid)
    if not student.resume_url:
        return jsonify({'message': 'No resume uploaded'}), 404
    return send_from_directory(UPLOAD_FOLDER, student.resume_url, as_attachment=False)

# --- DRIVES ---
@student_bp.route('/drives', methods=['GET'])
@student_required
@cache.cached(timeout=120, query_string=True) #cache purane applicant ka status for 2 mins to present student
def get_drives():
    q = request.args.get('q', '')
    s = current_user.student_profile

    query = PlacementDrive.query.filter_by(status='Approved')
    if q:
        # company name se bhi search hogi
        from models import Company
        matching_companies = Company.query.filter(Company.name.ilike(f'%{q}%')).all()
        company_ids = [c.id for c in matching_companies]
        query = query.filter(
            (PlacementDrive.job_title.ilike(f'%{q}%')) |
            (PlacementDrive.eligible_branches.ilike(f'%{q}%')) |
            (PlacementDrive.company_id.in_(company_ids))
        )

    drives = query.all()
    applied_ids = {a.drive_id for a in Application.query.filter_by(student_id=s.id).all()}

    result = []
    for d in drives:
        eligible = True
        if d.min_cgpa and s.cgpa < d.min_cgpa:
            eligible = False
        if d.eligible_year and s.year != d.eligible_year:
            eligible = False
        if d.eligible_branches:
            branches = [b.strip().lower() for b in d.eligible_branches.split(',')]
            if branches and (s.branch or '').strip().lower() not in branches:
                eligible = False

        result.append({
            'id': d.id,
            'job_title': d.job_title,
            'job_description': d.job_description,
            'company': d.company.name,
            'company_id': d.company_id,
            'eligible_branches': d.eligible_branches,
            'min_cgpa': d.min_cgpa,
            'eligible_year': d.eligible_year,
            'salary': d.salary,
            'location': d.location,
            'deadline': d.application_deadline.isoformat() if d.application_deadline else None,
            'status': d.status,
            'already_applied': d.id in applied_ids,
            'eligible': eligible,
            'applicants': len(d.applications)
        })

    return jsonify(result), 200

@student_bp.route('/apply/<int:did>', methods=['POST'])
@student_required
def apply(did):
    s = current_user.student_profile
    drive = PlacementDrive.query.get_or_404(did)

    if drive.status != 'Approved':
        return jsonify({'message': 'Drive not available'}), 400

    if drive.application_deadline and datetime.utcnow() > drive.application_deadline:
        return jsonify({'message': 'Application deadline passed'}), 400

    if drive.min_cgpa and s.cgpa < drive.min_cgpa:
        return jsonify({'message': f'Minimum CGPA {drive.min_cgpa} required'}), 400
    if drive.eligible_year and s.year != drive.eligible_year:
        return jsonify({'message': f'Only Year {drive.eligible_year} students eligible'}), 400
    if drive.eligible_branches:
        branches = [b.strip().lower() for b in drive.eligible_branches.split(',')]
        if branches and (s.branch or '').strip().lower() not in branches:
            return jsonify({'message': f'Only {drive.eligible_branches} branches eligible'}), 400

    existing = Application.query.filter_by(student_id=s.id, drive_id=did).first()
    if existing:
        return jsonify({'message': 'Already applied'}), 400

    app_obj = Application(student_id=s.id, drive_id=did)
    db.session.add(app_obj)
    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Applied successfully!'}), 201

# --- MY APPLICATIONS ---
@student_bp.route('/applications', methods=['GET'])
@student_required
def my_applications():
    s = current_user.student_profile
    apps = Application.query.filter_by(student_id=s.id).all()
    return jsonify([{
        'id': a.id,
        'drive_id': a.drive_id,
        'job_title': a.drive.job_title,
        'company': a.drive.company.name,
        'status': a.status,
        'feedback': a.feedback,
        'interview_date': a.interview_date.isoformat() if a.interview_date else None,
        'applied_at': a.applied_at.isoformat(),
        'salary': a.drive.salary
    } for a in apps]), 200

# --- CSV EXPORT (Async) ---
@student_bp.route('/export', methods=['POST'])
@student_required
def export_csv():
    from tasks import export_applications_csv
    s = current_user.student_profile
    
    # Trigger email notification task
    export_applications_csv.delay(s.id, current_user.email)
    
    # Generate CSV immediately for download
    from models import Application
    apps = Application.query.filter_by(student_id=s.id).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Application ID', 'Company Name', 'Drive Title', 'Status', 'Applied Date', 'Interview Date', 'Salary'])
    
    for a in apps:
        writer.writerow([
            a.id,
            a.drive.company.name,
            a.drive.job_title,
            a.status,
            a.applied_at.strftime('%d-%m-%Y'),
            a.interview_date.strftime('%d-%m-%Y') if a.interview_date else 'N/A',
            a.drive.salary or 'N/A'
        ])
    
    csv_content = output.getvalue()
    
    # Return CSV for immediate download
    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=my_applications.csv'
    return response
