from flask import Flask
from config import Config
from models import db, User, Role
from flask_security import Security, hash_password
from flask_cors import CORS
from extensions import user_datastore, celery, cache
from flask_wtf.csrf import CSRFProtect
import uuid

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app, supports_credentials=True)
    cache.init_app(app)

    # Must init CSRF before Security
    csrf.init_app(app)

    security = Security(app, user_datastore)

    with app.app_context():
        db.create_all()

        # Initialize roles and admin user
        from models import Role, User
        for role_name, desc in [('admin', 'Administrator'), ('company', 'Company'), ('student', 'Student')]:
            if not Role.query.filter_by(name=role_name).first():
                db.session.add(Role(name=role_name, description=desc))
        db.session.commit()

        if not User.query.filter_by(email='admin@gmail.com').first():
            user_datastore.create_user(
                email='admin@gmail.com',
                password=hash_password('1234'),
                fs_uniquifier=str(uuid.uuid4()),
                roles=['admin']
            )
            db.session.commit()

    # Register Blueprints
    from api.auth import auth_bp
    from api.admin import admin_bp
    from api.company import company_bp
    from api.student import student_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')

    # Exempt all API blueprints from CSRF (we use token auth)
    csrf.exempt(auth_bp)
    csrf.exempt(admin_bp)
    csrf.exempt(company_bp)
    csrf.exempt(student_bp)

    # Celery config
    celery.conf.broker_url = app.config['CELERY_BROKER_URL']
    celery.conf.result_backend = app.config['CELERY_RESULT_BACKEND']
    celery.conf.timezone = app.config['CELERY_TIMEZONE']

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return app

app = create_app()
import tasks

if __name__ == '__main__':
    app.run(debug=True, port=5001)
