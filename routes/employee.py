from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from extensions import db
from models import Attendance, Leave, Salary
from routes.utils import employee_required

employee_bp = Blueprint("employee", __name__, url_prefix="/employee")


def _current_employee():
    return current_user.employee


@employee_bp.route("/dashboard")
@login_required
@employee_required
def dashboard():
    e = _current_employee()
    return render_template(
        "employee/dashboard.html",
        employee=e,
        today_attendance=Attendance.query.filter_by(employee_id=e.id, date=date.today()).first(),
        pending_leaves=Leave.query.filter_by(employee_id=e.id, status="pending").count()
    )


@employee_bp.route("/profile")
@login_required
@employee_required
def profile():
    return render_template("employee/profile.html", employee=_current_employee())


@employee_bp.route("/attendance", methods=["GET", "POST"])
@login_required
@employee_required
def attendance():
    e = _current_employee()

    if request.method == "POST":
        today = date.today()
        if Attendance.query.filter_by(employee_id=e.id, date=today).first():
            flash("You have already marked attendance for today.", "warning")
        else:
            db.session.add(Attendance(employee_id=e.id, date=today, status="present"))
            db.session.commit()
            flash("Attendance marked for today.", "success")
        return redirect(url_for("employee.attendance"))

    records = Attendance.query.filter_by(employee_id=e.id).order_by(Attendance.date.desc()).all()
    return render_template("employee/attendance.html", records=records)


@employee_bp.route("/leave", methods=["GET", "POST"])
@login_required
@employee_required
def leave():
    e = _current_employee()

    if request.method == "POST":
        f = request.form
        db.session.add(Leave(
            employee_id=e.id,
            leave_type=f.get("leave_type", "").strip(),
            start_date=f.get("start_date"),
            end_date=f.get("end_date"),
            reason=f.get("reason", "").strip()
        ))
        db.session.commit()
        flash("Leave request submitted.", "success")
        return redirect(url_for("employee.leave"))

    records = Leave.query.filter_by(employee_id=e.id).order_by(Leave.applied_on.desc()).all()
    return render_template("employee/leave.html", leave_history=records)


@employee_bp.route("/salary")
@login_required
@employee_required
def salary():
    e = _current_employee()
    records = Salary.query.filter_by(employee_id=e.id).order_by(
        Salary.year.desc(), Salary.month.desc()
    ).all()
    return render_template("employee/salary.html", records=records)