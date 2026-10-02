from app import app
from extensions import db
from models import User

with app.app_context():
    if User.query.filter_by(username="hr").first():
        print("HR user already exists.")
    else:
        user = User(username="hr", email="hr@example.com", role="hr")
        user.set_password("HR@12345")
        db.session.add(user)
        db.session.commit()
        print("HR user created successfully.")