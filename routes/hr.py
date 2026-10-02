import os, re
from datetime import date
from flask import Blueprint, render_template, request, abort, send_from_directory
from flask_login import login_required, current_user
from models import Employee, Attendance, Leave

hr_bp = Blueprint("hr", __name__, url_prefix="/hr")


@hr_bp.before_request
@login_required
def require_hr():
    if current_user.role != "hr":
        abort(403)


@hr_bp.route("/dashboard")
def dashboard():
    return render_template("hr/dashboard.html",
        employee_count=Employee.query.count(),
        pending_leaves=Leave.query.filter_by(status="pending").count(),
        present_today=Attendance.query.filter_by(date=date.today(), status="present").count())


@hr_bp.route("/employees")
def employees():
    return render_template("hr/employees.html",
        employees=Employee.query.order_by(Employee.full_name).all())


@hr_bp.route("/employees/<int:employee_id>")
def employee_details(employee_id):
    return render_template("hr/employee_details.html",
        employee=Employee.query.get_or_404(employee_id))


@hr_bp.route("/attendance")
def attendance():
    d = request.args.get("date") or date.today().isoformat()
    records = Attendance.query.filter_by(date=d).join(Employee).order_by(Employee.full_name).all()
    return render_template("hr/attendance.html", records=records, selected_date=d)


@hr_bp.route("/leaves")
def leaves():
    status = request.args.get("status", "pending")
    query = Leave.query.join(Employee)
    if status != "all":
        query = query.filter(Leave.status == status)
    return render_template("hr/leaves.html",
        leaves=query.order_by(Leave.applied_on.desc()).all(), status_filter=status)


def normalize(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def find_file(employee, folder_name):
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    name = normalize(employee.full_name)

    for folder in [
        os.path.join(root, "Stored Data", folder_name),
        os.path.join(root, "stored_data", folder_name),
        os.path.join(root, "stored_data", folder_name.lower())
    ]:
        if not os.path.isdir(folder):
            continue

        for filename in os.listdir(folder):
            if not filename.lower().endswith(".pdf"):
                continue

            file_name = filename
            while file_name.lower().endswith(".pdf"):
                file_name = file_name[:-4]

            file_name = normalize(file_name)

            if file_name == name or file_name in name or name in file_name:
                return folder, filename

    return None, None


@hr_bp.route("/resumes")
def resumes():
    data = [
        {"employee": e, "filename": find_file(e, "Resumes")[1]}
        for e in Employee.query.order_by(Employee.full_name).all()
    ]
    return render_template("hr/resumes.html", employee_resumes=data)


@hr_bp.route("/resumes/<int:employee_id>")
def view_resume(employee_id):
    folder, filename = find_file(
        Employee.query.get_or_404(employee_id), "Resumes"
    )
    if not filename:
        abort(404)
    return send_from_directory(folder, filename)


@hr_bp.route("/offer-letters")
def offer_letters():
    data = [
        {"employee": e, "filename": find_file(e, "Offer Letters")[1]}
        for e in Employee.query.order_by(Employee.full_name).all()
    ]
    return render_template("hr/offer_letters.html", employee_offer_letters=data)


@hr_bp.route("/offer-letters/<int:employee_id>")
def view_offer_letter(employee_id):
    folder, filename = find_file(
        Employee.query.get_or_404(employee_id), "Offer Letters"
    )
    if not filename:
        abort(404)
    return send_from_directory(folder, filename)