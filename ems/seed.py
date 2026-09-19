"""
Run once after the database tables are created:

    python seed.py

Creates all tables (if they don't already exist), one admin account,
and one sample department, so you have somewhere to start.
"""
from app import app
from extensions import db
from models import Department, User

with app.app_context():
    db.create_all()

    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", email="admin@example.com", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)

    if not Department.query.filter_by(name="General").first():
        db.session.add(Department(name="General", description="Default department"))

    db.session.commit()
    print("Seed complete.")
    print("Admin login -> username: admin / password: admin123")
    print("Change this password immediately in a real deployment.")
