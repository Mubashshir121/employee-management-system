from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from extensions import db
from models import Department, Employee, User

auth_bp = Blueprint("auth", __name__)


def _redirect_home(user):
    if user.is_admin():
        return redirect(url_for("admin.dashboard"))
    if user.is_hr():
        return redirect(url_for("hr.dashboard"))
    return redirect(url_for("employee.dashboard"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirect_home(current_user)

    if request.method == "POST":
        f = request.form
        user = User.query.filter_by(username=f.get("username", "").strip()).first()

        if user and user.check_password(f.get("password", "")):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            return _redirect_home(user)

        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return _redirect_home(current_user)

    departments = Department.query.order_by(Department.name).all()

    if request.method == "POST":
        f = request.form
        username = f.get("username", "").strip()
        email = f.get("email", "").strip()

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already in use.", "danger")
            return render_template("auth/register.html", departments=departments)

        user = User(username=username, email=email, role="employee")
        user.set_password(f.get("password", ""))
        db.session.add(user)
        db.session.flush()

        last = Employee.query.order_by(Employee.id.desc()).first()
        employee = Employee(
            user_id=user.id,
            employee_code=f"EMP{(last.id + 1 if last else 1):04d}",
            full_name=f.get("full_name", "").strip(),
            phone=f.get("phone", "").strip(),
            designation=f.get("designation", "").strip(),
            department_id=f.get("department_id") or None
        )

        db.session.add(employee)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", departments=departments)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))