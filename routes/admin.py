from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from extensions import db
from models import Attendance, Department, Employee, Leave, Salary, User
from routes.utils import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    stats = {
        "employee_count": Employee.query.count(),
        "department_count": Department.query.count(),
        "pending_leaves": Leave.query.filter_by(status="pending").count(),
        "present_today": Attendance.query.filter_by(date=date.today(), status="present").count(),
    }
    recent_leaves = Leave.query.order_by(Leave.applied_on.desc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, recent_leaves=recent_leaves)


# ---------- Employees ----------

@admin_bp.route("/employees")
@login_required
@admin_required
def employees():
    all_employees = Employee.query.order_by(Employee.id).all()
    departments = Department.query.order_by(Department.name).all()

    return render_template(
        "admin/employees.html",
        employees=all_employees,
        departments=departments
    )


@admin_bp.route("/employees/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_employee():
    departments = Department.query.order_by(Department.name).all()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        designation = request.form.get("designation", "").strip()
        department_id = request.form.get("department_id") or None

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already in use.", "danger")
            return render_template("admin/employee_form.html", departments=departments, employee=None)

        user = User(username=username, email=email, role="employee")
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        last = Employee.query.order_by(Employee.id.desc()).first()
        next_num = (last.id + 1) if last else 1

        employee = Employee(
            user_id=user.id,
            employee_code=f"EMP{next_num:04d}",
            full_name=full_name,
            phone=phone,
            address=address,
            designation=designation,
            department_id=department_id,
        )
        db.session.add(employee)
        db.session.commit()
        flash("Employee added.", "success")
        return redirect(url_for("admin.employees"))

    return render_template("admin/employee_form.html", departments=departments, employee=None)


@admin_bp.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    departments = Department.query.order_by(Department.name).all()

    if request.method == "POST":
        employee.full_name = request.form.get("full_name", "").strip()
        employee.phone = request.form.get("phone", "").strip()
        employee.address = request.form.get("address", "").strip()
        employee.designation = request.form.get("designation", "").strip()
        employee.department_id = request.form.get("department_id") or None
        db.session.commit()
        flash("Employee updated.", "success")
        return redirect(url_for("admin.employees"))

    return render_template("admin/employee_form.html", departments=departments, employee=employee)


@admin_bp.route("/employees/<int:employee_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    user = employee.user
    db.session.delete(employee)
    db.session.delete(user)
    db.session.commit()
    flash("Employee deleted.", "info")
    return redirect(url_for("admin.employees"))


# ---------- Departments ----------

@admin_bp.route("/departments", methods=["GET", "POST"])
@login_required
@admin_required
def departments():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if name and not Department.query.filter_by(name=name).first():
            db.session.add(Department(name=name, description=description))
            db.session.commit()
            flash("Department added.", "success")
        else:
            flash("Department name is required and must be unique.", "danger")
        return redirect(url_for("admin.departments"))

    all_departments = Department.query.order_by(Department.name).all()
    return render_template("admin/departments.html", departments=all_departments)


@admin_bp.route("/departments/<int:department_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_department(department_id):
    department = Department.query.get_or_404(department_id)
    db.session.delete(department)
    db.session.commit()
    flash("Department deleted.", "info")
    return redirect(url_for("admin.departments"))


# ---------- Attendance ----------

@admin_bp.route("/attendance")
@login_required
@admin_required
def attendance():
    selected_date = request.args.get("date") or date.today().isoformat()
    records = (
        Attendance.query.filter_by(date=selected_date)
        .join(Employee)
        .order_by(Employee.full_name)
        .all()
    )
    all_employees = Employee.query.order_by(Employee.full_name).all()
    marked_ids = {r.employee_id for r in records}
    unmarked = [e for e in all_employees if e.id not in marked_ids]
    return render_template(
        "admin/attendance.html", records=records, unmarked=unmarked, selected_date=selected_date
    )


@admin_bp.route("/attendance/mark", methods=["POST"])
@login_required
@admin_required
def mark_attendance():
    employee_id = request.form.get("employee_id")
    status = request.form.get("status", "present")
    att_date = request.form.get("date") or date.today().isoformat()

    existing = Attendance.query.filter_by(employee_id=employee_id, date=att_date).first()
    if existing:
        existing.status = status
    else:
        db.session.add(Attendance(employee_id=employee_id, date=att_date, status=status))
    db.session.commit()
    flash("Attendance recorded.", "success")
    return redirect(url_for("admin.attendance", date=att_date))


# ---------- Leaves ----------

@admin_bp.route("/leaves")
@login_required
@admin_required
def leaves():
    status_filter = request.args.get("status", "pending")
    query = Leave.query.join(Employee)
    if status_filter != "all":
        query = query.filter(Leave.status == status_filter)
    all_leaves = query.order_by(Leave.applied_on.desc()).all()
    return render_template("admin/leaves.html", leaves=all_leaves, status_filter=status_filter)


@admin_bp.route("/leaves/<int:leave_id>/<string:decision>", methods=["POST"])
@login_required
@admin_required
def decide_leave(leave_id, decision):
    if decision not in ("approved", "rejected"):
        flash("Invalid decision.", "danger")
        return redirect(url_for("admin.leaves"))

    leave = Leave.query.get_or_404(leave_id)
    leave.status = decision
    db.session.commit()
    flash(f"Leave request {decision}.", "success")
    return redirect(url_for("admin.leaves"))


# ---------- Salary ----------

@admin_bp.route("/salary/<int:employee_id>", methods=["GET", "POST"])
@login_required
@admin_required
def salary(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    if request.method == "POST":
        month = int(request.form.get("month"))
        year = int(request.form.get("year"))
        basic = float(request.form.get("basic", 0))
        allowances = float(request.form.get("allowances", 0))
        deductions = float(request.form.get("deductions", 0))
        net = basic + allowances - deductions

        record = Salary.query.filter_by(employee_id=employee_id, month=month, year=year).first()
        if not record:
            record = Salary(employee_id=employee_id, month=month, year=year)
            db.session.add(record)

        record.basic = basic
        record.allowances = allowances
        record.deductions = deductions
        record.net_salary = net
        record.paid_on = date.today()
        db.session.commit()
        flash("Salary record saved.", "success")
        return redirect(url_for("admin.salary", employee_id=employee_id))

    records = Salary.query.filter_by(employee_id=employee_id).order_by(
        Salary.year.desc(), Salary.month.desc()
    ).all()
    return render_template("admin/salary.html", employee=employee, records=records)


# ---------- Reports ----------

@admin_bp.route("/reports")
@login_required
@admin_required
def reports():
    # Employees by department
    dept_counts = (
        db.session.query(Department.name, db.func.count(Employee.id))
        .outerjoin(Employee)
        .group_by(Department.name)
        .all()
    )

    # Leave status distribution
    leave_counts = (
        db.session.query(Leave.status, db.func.count(Leave.id))
        .group_by(Leave.status)
        .all()
    )

    # Attendance status distribution
    attendance_counts = (
        db.session.query(Attendance.status, db.func.count(Attendance.id))
        .group_by(Attendance.status)
        .all()
    )

    # Monthly attendance
    monthly_attendance = (
        db.session.query(
            db.func.date_format(Attendance.date, "%Y-%m"),
            db.func.count(Attendance.id)
        )
        .group_by(db.func.date_format(Attendance.date, "%Y-%m"))
        .order_by(db.func.date_format(Attendance.date, "%Y-%m"))
        .all()
    )

    # Total net salary
    total_net_salary = db.session.query(
        db.func.coalesce(db.func.sum(Salary.net_salary), 0)
    ).scalar()

    return render_template(
        "admin/reports.html",
        dept_counts=dept_counts,
        leave_counts=leave_counts,
        attendance_counts=attendance_counts,
        monthly_attendance=monthly_attendance,
        total_net_salary=total_net_salary,
    )

    # ---------- Employee Details ----------

@admin_bp.route("/employee-details")
@login_required
@admin_required
def employee_details():
    all_employees = Employee.query.order_by(Employee.full_name).all()

    return render_template(
        "admin/employee_details.html",
        employees=all_employees
    )

    # ---------- Employee Profile ----------

@admin_bp.route("/employee-details/<int:employee_id>")
@login_required
@admin_required
def employee_profile(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    salary_records = (
        Salary.query
        .filter_by(employee_id=employee.id)
        .order_by(Salary.year.desc(), Salary.month.desc())
        .all()
    )

    attendance_records = (
        Attendance.query
        .filter_by(employee_id=employee.id)
        .order_by(Attendance.date.desc())
        .all()
    )

    leave_records = (
        Leave.query
        .filter_by(employee_id=employee.id)
        .order_by(Leave.applied_on.desc())
        .all()
    )

    return render_template(
        "admin/employee_profile.html",
        employee=employee,
        salary_records=salary_records,
        attendance_records=attendance_records,
        leave_records=leave_records,
    )