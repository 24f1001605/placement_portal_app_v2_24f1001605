from app import create_app
from models import db, User
app = create_app()
with app.app_context():
    users = User.query.all()
    for u in users:
        print(f"User: {u.email} active: {u.active}")
