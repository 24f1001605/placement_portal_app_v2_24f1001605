from app import create_app
from models import db, User
from flask_security import hash_password

app = create_app()
with app.app_context():
    users = User.query.all()
    print("Resetting passwords for all users...")
    for u in users:
        u.password = hash_password('1234')
        u.active = True  # Ensure they are active so you can log in
        print(f"Password reset for: {u.email} (Password set to: 1234)")
    db.session.commit()
    print("All passwords successfully reset to '1234'!")
