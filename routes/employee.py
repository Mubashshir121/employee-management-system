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
    employee = _current_employee()
    today_attendance = Attendance.query.filter_by(employee_id=employee.id, date=date.today()).first()
    pending_leaves = Leave.query.filter_by(employee_id=employee.id, status="pending").count()
    return render_template(
        "employee/dashboard.html", employee=employee, today_attendance=today_attendance,
        pending_leaves=pending_leaves,
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
    employee = _current_employee()

    if request.method == "POST":
        today = date.today()
        existing = Attendance.query.filter_by(employee_id=employee.id, date=today).first()
        if existing:
            flash("You have already marked attendance for today.", "warning")
        else:
            db.session.add(Attendance(employee_id=employee.id, date=today, status="present"))
            db.session.commit()
            flash("Attendance marked for today.", "success")
        return redirect(url_for("employee.attendance"))

    records = (
        Attendance.query.filter_by(employee_id=employee.id).order_by(Attendance.date.desc()).all()
    )
    return render_template("employee/attendance.html", records=records)


@employee_bp.route("/leave", methods=["GET", "POST"])
@login_required
@employee_required
def leave():
    employee = _current_employee()

    if request.method == "POST":
        leave_type = request.form.get("leave_type", "").strip()
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        reason = request.form.get("reason", "").strip()

        db.session.add(
            Leave(
                employee_id=employee.id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
            )
        )
        db.session.commit()
        flash("Leave request submitted.", "success")
        return redirect(url_for("employee.leave"))

    leave_history = (
        Leave.query.filter_by(employee_id=employee.id).order_by(Leave.applied_on.desc()).all()
    )
    return render_template("employee/leave.html", leave_history=leave_history)


@employee_bp.route("/salary")
@login_required
@employee_required
def salary():
    employee = _current_employee()
    records = (
        Salary.query.filter_by(employee_id=employee.id)
        .order_by(Salary.year.desc(), Salary.month.desc())
        .all()
    )
    return render_template("employee/salary.html", records=records)
