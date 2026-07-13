from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from models import db, PlacementDrive, Application, Student
from datetime import datetime
from extensions import cache
import os

company_bp = Blueprint('company', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')

def company_required(f):
    from functools import wraps
    @wraps(f)
    @auth_required('token', 'session')
    def decorated(*args, **kwargs):
        if not current_user.has_role('company'):
            return jsonify({'message': 'Company access required'}), 403
        if not current_user.company_profile or current_user.company_profile.approval_status != 'Approved':
            return jsonify({'message': 'Company not approved'}), 403
        return f(*args, **kwargs)
    return decorated

@company_bp.route('/dashboard', methods=['GET'])
@company_required
def dashboard():
    c = current_user.company_profile
    drives = PlacementDrive.query.filter_by(company_id=c.id).all()
    total_applicants = sum(len(d.applications) for d in drives)
    shortlisted = sum(1 for d in drives for a in d.applications if a.status == 'Shortlisted')
    selected = sum(1 for d in drives for a in d.applications if a.status == 'Selected')

    return jsonify({
        'company': {
            'id': c.id,
            'name': c.name,
            'industry': c.industry,
            'website': c.website,
            'hr_contact': c.hr_contact,
            'location': c.location,
            'description': c.description
        },
        'total_drives': len(drives),
        'total_applicants': total_applicants,
        'shortlisted': shortlisted,
        'selected': selected
    }), 200


@company_bp.route('/drives', methods=['GET'])
@company_required
def get_drives():
    c = current_user.company_profile
    drives = PlacementDrive.query.filter_by(company_id=c.id).all()
    return jsonify([{
        'id': d.id,
        'job_title': d.job_title,
        'job_description': d.job_description,
        'eligible_branches': d.eligible_branches,
        'min_cgpa': d.min_cgpa,
        'eligible_year': d.eligible_year,
        'salary': d.salary,
        'location': d.location,
        'deadline': d.application_deadline.strftime('%Y-%m-%d')if d.application_deadline else None,
        'status': d.status,
        'applicants': len(d.applications)
    } for d in drives]), 200

@company_bp.route('/drives', methods=['POST'])
@company_required
def create_drive():
    c = current_user.company_profile
    data = request.get_json()

    deadline = None
    if data.get('application_deadline'):
        deadline = datetime.fromisoformat(data['application_deadline'])

    drive = PlacementDrive(
        company_id=c.id,
        job_title=data.get('job_title'),
        job_description=data.get('job_description', ''),
        eligible_branches=data.get('eligible_branches', ''),
        min_cgpa=float(data.get('min_cgpa', 0.0)),
        eligible_year=int(data.get('eligible_year', 0)) if data.get('eligible_year') else None,
        salary=float(data.get('salary', 0.0)),
        location=data.get('location', ''),
        application_deadline=deadline,
        status='Pending'
    )
    db.session.add(drive)
    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Drive created. Awaiting admin approval.'}), 201

@company_bp.route('/drives/<int:did>/close', methods=['POST'])
@company_required
def close_drive(did):
    drive = PlacementDrive.query.get_or_404(did)
    if drive.company_id != current_user.company_profile.id:
        return jsonify({'message': 'Unauthorized'}), 403
    drive.status = 'Closed'
    db.session.commit()
    return jsonify({'message': 'Drive closed'}), 200


@company_bp.route('/drives/<int:did>/applications', methods=['GET'])
@company_required
def get_applications(did):
    drive = PlacementDrive.query.get_or_404(did)
    if drive.company_id != current_user.company_profile.id:
        return jsonify({'message': 'Unauthorized'}), 403

    apps = Application.query.filter_by(drive_id=did).all()
    return jsonify([{
        'id': a.id,
        'student_id': a.student_id,
        'student_name': a.student.name,
        'branch': a.student.branch,
        'cgpa': a.student.cgpa,
        'year': a.student.year,
        'skills': a.student.skills,
        'contact': a.student.contact,
        'email': a.student.user.email,
        'resume_url': a.student.resume_url,
        'status': a.status,
        'feedback': a.feedback,
        'interview_date': a.interview_date.strftime('%Y-%m-%d')if a.interview_date else None,
        'applied_at': a.applied_at.strftime('%Y-%m-%d')
    } for a in apps]), 200

# --- UPDATE APPLICATION STATUS + FEEDBACK + INTERVIEW DATE ---
@company_bp.route('/applications/<int:aid>/update', methods=['POST'])
@company_required
def update_application(aid):
    app_obj = Application.query.get_or_404(aid)
    # Security: make sure this application belongs to company's drive
    if app_obj.drive.company_id != current_user.company_profile.id:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    if data.get('status'):
        app_obj.status = data['status']
    if 'feedback' in data:
        app_obj.feedback = data['feedback']
    if data.get('interview_date'):
        try:
            app_obj.interview_date = datetime.fromisoformat(data['interview_date'])
        except ValueError:
            return jsonify({'message': 'Invalid interview date format'}), 400

    db.session.commit()
    return jsonify({'message': 'Application updated successfully'}), 200

# company can view student resume
@company_bp.route('/resume/<int:sid>', methods=['GET'])
@company_required
def view_resume(sid):
    from flask import send_from_directory
    student = Student.query.get_or_404(sid)
    if not student.resume_url:
        return jsonify({'message': 'Student has not uploaded a resume'}), 404
    return send_from_directory(UPLOAD_FOLDER, student.resume_url, as_attachment=False)
