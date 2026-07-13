from app import create_app
from models import db, User, Role
from extensions import user_datastore
from flask_security import hash_password
import uuid

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='admin@gmail.com').first()
    if user:
        user.password = hash_password('1234')
        user.active = True
        db.session.commit()
        print('Admin password reset successful.')
    else:
        user_datastore.create_user(
            email='admin@gmail.com',
            password=hash_password('1234'),
            fs_uniquifier=str(uuid.uuid4()),
            roles=['admin']
        )
        db.session.commit()
        print('Admin user created fresh.')
