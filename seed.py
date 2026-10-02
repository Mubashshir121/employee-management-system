from app import app
from extensions import db
from models import Department, User

with app.app_context():
    db.create_all()

    if not User.query.filter_by(username="admin").first():
        user = User(username="admin", email="admin@example.com", role="admin")
        user.set_password("admin123")
        db.session.add(user)

    if not Department.query.filter_by(name="General").first():
        db.session.add(Department(name="General", description="Default department"))

    db.session.commit()
    print("Seed complete.")