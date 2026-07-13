from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime

db = SQLAlchemy()

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(255), unique=True)
    password      = db.Column(db.String(255))
    active        = db.Column(db.Boolean, default=True)
    confirmed_at  = db.Column(db.DateTime)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles         = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    company_profile = db.relationship('Company', backref='user', uselist=False)
    student_profile = db.relationship('Student', backref='user', uselist=False)

class Company(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name            = db.Column(db.String(150), nullable=False)
    industry        = db.Column(db.String(100))
    website         = db.Column(db.String(255))
    hr_contact      = db.Column(db.String(100))
    location        = db.Column(db.String(150))
    description     = db.Column(db.Text)
    approval_status = db.Column(db.String(20), default='Pending')  
    is_active       = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    drives = db.relationship('PlacementDrive', backref='company', lazy=True, cascade='all, delete-orphan')

class Student(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name           = db.Column(db.String(100), nullable=False)
    branch         = db.Column(db.String(100))
    cgpa           = db.Column(db.Float, default=0.0)
    year           = db.Column(db.Integer)
    contact        = db.Column(db.String(20))
    address        = db.Column(db.String(255))
    skills         = db.Column(db.Text)   # comma-separated
    resume_url     = db.Column(db.String(500))
    is_active      = db.Column(db.Boolean, default=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')

class PlacementDrive(db.Model):
    id                 = db.Column(db.Integer, primary_key=True)
    company_id         = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    job_title          = db.Column(db.String(150), nullable=False)
    job_description    = db.Column(db.Text)
    eligible_branches  = db.Column(db.String(255))   # comma-separated
    min_cgpa           = db.Column(db.Float, default=0.0)
    eligible_year      = db.Column(db.Integer)
    salary             = db.Column(db.Float)
    location           = db.Column(db.String(150))
    application_deadline = db.Column(db.DateTime)
    status             = db.Column(db.String(20), default='Pending')  
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='drive', lazy=True, cascade='all, delete-orphan')

class Application(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    student_id   = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id     = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    applied_at   = db.Column(db.DateTime, default=datetime.utcnow)
    status       = db.Column(db.String(20), default='Applied')  
    feedback     = db.Column(db.Text)
    interview_date = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),)
