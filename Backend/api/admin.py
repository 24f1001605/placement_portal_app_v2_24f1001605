from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from models import db, User, Company, Student, PlacementDrive, Application
from extensions import cache

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    @auth_required('token', 'session')
    def decorated(*args, **kwargs):
        if not current_user.has_role('admin'):
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    total_students = Student.query.filter_by(is_active=True).count()
    total_companies = Company.query.filter_by(is_active=True).count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    pending_companies = Company.query.filter_by(approval_status='Pending').count()
    pending_drives = PlacementDrive.query.filter_by(status='Pending').count()
    placed_students = Application.query.filter_by(status='Selected').count()

    return jsonify({
        'total_students': total_students,
        'total_companies': total_companies,
        'total_drives': total_drives,
        'total_applications': total_applications,
        'pending_companies': pending_companies,
        'pending_drives': pending_drives,
        'placed_students': placed_students,
    }), 200


@admin_bp.route('/companies', methods=['GET'])
@admin_required
@cache.cached(timeout=60, query_string=True)
def get_companies():
    q = request.args.get('q', '')
    query = Company.query
    if q:
        query = query.filter(Company.name.ilike(f'%{q}%'))
    companies = query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'industry': c.industry,
        'website': c.website,
        'hr_contact': c.hr_contact,
        'location': c.location,
        'approval_status': c.approval_status,
        'is_active': c.is_active,
        'email': c.user.email
    } for c in companies]), 200

@admin_bp.route('/companies/<int:cid>/approve', methods=['POST'])
@admin_required
def approve_company(cid):
    company = Company.query.get_or_404(cid)
    company.approval_status = 'Approved'
    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Company approved'}), 200

@admin_bp.route('/companies/<int:cid>/reject', methods=['POST'])
@admin_required
def reject_company(cid):
    company = Company.query.get_or_404(cid)
    company.approval_status = 'Rejected'
    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Company rejected'}), 200

@admin_bp.route('/companies/<int:cid>/toggle', methods=['POST'])
@admin_required
def toggle_company(cid):
    company = Company.query.get_or_404(cid)
    company.is_active = not company.is_active
    company.user.active = company.is_active
    db.session.commit()
    cache.clear()
    status = 'activated' if company.is_active else 'blacklisted'
    return jsonify({'message': f'Company {status}'}), 200


@admin_bp.route('/students', methods=['GET'])
@admin_required
@cache.cached(timeout=60, query_string=True)
def get_students():
    q = request.args.get('q', '')
    query = Student.query
    if q:
        query = query.filter(Student.name.ilike(f'%{q}%'))
    students = query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'branch': s.branch,
        'cgpa': s.cgpa,
        'year': s.year,
        'contact': s.contact,
        'skills': s.skills,
        'is_active': s.is_active,
        'email': s.user.email
    } for s in students]), 200

@admin_bp.route('/students/<int:sid>/toggle', methods=['POST'])
@admin_required
def toggle_student(sid):
    student = Student.query.get_or_404(sid)
    student.is_active = not student.is_active
    student.user.active = student.is_active
    db.session.commit()
    cache.clear()
    status = 'activated' if student.is_active else 'deactivated'
    return jsonify({'message': f'Student {status}'}), 200


@admin_bp.route('/drives', methods=['GET'])
@admin_required
def get_drives():
    drives = PlacementDrive.query.all()
    return jsonify([{
        'id': d.id,
        'job_title': d.job_title,
        'company': d.company.name,
        'company_id': d.company_id,
        'status': d.status,
        'deadline': d.application_deadline.isoformat() if d.application_deadline else None,
        'salary': d.salary,
        'applicants': len(d.applications)
    } for d in drives]), 200

@admin_bp.route('/drives/<int:did>/approve', methods=['POST'])
@admin_required
def approve_drive(did):
    drive = PlacementDrive.query.get_or_404(did)
    drive.status = 'Approved'
    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Drive approved'}), 200

@admin_bp.route('/drives/<int:did>/reject', methods=['POST'])
@admin_required
def reject_drive(did):
    drive = PlacementDrive.query.get_or_404(did)
    drive.status = 'Rejected'
    db.session.commit()
    cache.clear()
    return jsonify({'message': 'Drive rejected'}), 200


@admin_bp.route('/applications', methods=['GET'])
@admin_required
def get_applications():
    apps = Application.query.all()
    return jsonify([{
        'id': a.id,
        'student': a.student.name,
        'drive': a.drive.job_title,
        'company': a.drive.company.name,
        'status': a.status,
        'applied_at': a.applied_at.isoformat()
    } for a in apps]), 200

@admin_bp.route('/placed-students', methods=['GET'])
@admin_required
def get_placed_students():
    apps = Application.query.filter_by(status='Selected').all()
    return jsonify([{
        'id': a.id,
        'student': a.student.name,
        'drive': a.drive.job_title,
        'company': a.drive.company.name,
        'salary': a.drive.salary,
        'placed_on': a.applied_at.isoformat()
    } for a in apps]), 200
