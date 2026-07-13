from flask import Blueprint, request, jsonify
from flask_security import login_user, logout_user, current_user, hash_password
from models import db, User, Student, Company
from extensions import user_datastore
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = user_datastore.find_user(email=email)
    if not user or not user.active:
        return jsonify({'message': 'Invalid credentials or account deactivated'}), 401

    from flask_security.utils import verify_password
    if not verify_password(password, user.password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Check company approval
    if user.has_role('company'):
        if user.company_profile and user.company_profile.approval_status != 'Approved':
            return jsonify({'message': 'Company not approved by admin yet'}), 403

    login_user(user)
    token = user.get_auth_token()
    roles = [r.name for r in user.roles]

    resp = {
        'token': token,
        'email': user.email,
        'role': roles[0] if roles else '',
        'id': user.id
    }

    if user.company_profile:
        resp['name'] = user.company_profile.name
        resp['company_id'] = user.company_profile.id
    elif user.student_profile:
        resp['name'] = user.student_profile.name
        resp['student_id'] = user.student_profile.id
    else:
        resp['name'] = 'Admin'

    return jsonify(resp), 200

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return jsonify({'message': 'All fields required'}), 400

    if user_datastore.find_user(email=email):
        return jsonify({'message': 'Email already registered'}), 400

    user = user_datastore.create_user(
        email=email,
        password=hash_password(password),
        fs_uniquifier=str(uuid.uuid4()),
        roles=['student']
    )
    db.session.flush()

    cgpa = float(data.get('cgpa') or 0.0)
    year = int(data.get('year') or 1)
    student = Student(
        user_id=user.id,
        name=name,
        branch=data.get('branch', ''),
        cgpa=cgpa,
        year=year,
        contact=data.get('contact', ''),
        skills=data.get('skills', '')
    )
    db.session.add(student)
    db.session.commit()

    return jsonify({'message': 'Student registered successfully'}), 201

@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return jsonify({'message': 'All fields required'}), 400

    if user_datastore.find_user(email=email):
        return jsonify({'message': 'Email already registered'}), 400

    user = user_datastore.create_user(
        email=email,
        password=hash_password(password),
        fs_uniquifier=str(uuid.uuid4()),
        roles=['company']
    )
    db.session.flush()

    company = Company(
        user_id=user.id,
        name=name,
        industry=data.get('industry', ''),
        website=data.get('website', ''),
        hr_contact=data.get('hr_contact', ''),
        location=data.get('location', ''),
        description=data.get('description', ''),
        approval_status='Pending'
    )
    db.session.add(company)
    db.session.commit()

    return jsonify({'message': 'Company registered. Awaiting admin approval.'}), 201

@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'}), 200
