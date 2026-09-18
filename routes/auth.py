from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db
from models import Department, Employee, User

auth_bp = Blueprint("auth", __name__)


def _redirect_home(user):
    return redirect(url_for("admin.dashboard") if user.is_admin() else url_for("employee.dashboard"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirect_home(current_user)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            return _redirect_home(user)

        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Self-service registration for employees only."""
    if current_user.is_authenticated:
        return _redirect_home(current_user)

    departments = Department.query.order_by(Department.name).all()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        department_id = request.form.get("department_id") or None
        designation = request.form.get("designation", "").strip()
        phone = request.form.get("phone", "").strip()

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already in use.", "danger")
            return render_template("auth/register.html", departments=departments)

        user = User(username=username, email=email, role="employee")
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # get user.id before commit

        last = Employee.query.order_by(Employee.id.desc()).first()
        next_num = (last.id + 1) if last else 1
        employee = Employee(
            user_id=user.id,
            employee_code=f"EMP{next_num:04d}",
            full_name=full_name,
            phone=phone,
            designation=designation,
            department_id=department_id,
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
