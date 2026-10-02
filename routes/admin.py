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
    stats={"employee_count":Employee.query.count(),"department_count":Department.query.count(),"pending_leaves":Leave.query.filter_by(status="pending").count(),"present_today":Attendance.query.filter_by(date=date.today(),status="present").count()}
    return render_template("admin/dashboard.html",stats=stats,recent_leaves=Leave.query.order_by(Leave.applied_on.desc()).limit(5).all())


@admin_bp.route("/employees")
@login_required
@admin_required
def employees():
    return render_template("admin/employees.html",employees=Employee.query.order_by(Employee.id).all())


@admin_bp.route("/employees/add",methods=["GET","POST"])
@login_required
@admin_required
def add_employee():
    departments=Department.query.order_by(Department.name).all()
    if request.method=="POST":
        f=request.form; username=f.get("username","").strip(); email=f.get("email","").strip()
        if User.query.filter((User.username==username)|(User.email==email)).first():
            flash("Username or email already in use.","danger")
            return render_template("admin/employee_form.html",departments=departments,employee=None)
        user=User(username=username,email=email,role="employee"); user.set_password(f.get("password","")); db.session.add(user); db.session.flush()
        last=Employee.query.order_by(Employee.id.desc()).first()
        db.session.add(Employee(user_id=user.id,employee_code=f"EMP{(last.id+1 if last else 1):04d}",full_name=f.get("full_name","").strip(),phone=f.get("phone","").strip(),address=f.get("address","").strip(),designation=f.get("designation","").strip(),department_id=f.get("department_id") or None))
        db.session.commit(); flash("Employee added.","success")
        return redirect(url_for("admin.employees"))
    return render_template("admin/employee_form.html",departments=departments,employee=None)


@admin_bp.route("/employees/<int:employee_id>/edit",methods=["GET","POST"])
@login_required
@admin_required
def edit_employee(employee_id):
    employee=Employee.query.get_or_404(employee_id); departments=Department.query.order_by(Department.name).all()
    if request.method=="POST":
        f=request.form
        employee.full_name=f.get("full_name","").strip(); employee.phone=f.get("phone","").strip(); employee.address=f.get("address","").strip(); employee.designation=f.get("designation","").strip(); employee.department_id=f.get("department_id") or None
        db.session.commit(); flash("Employee updated.","success")
        return redirect(url_for("admin.employees"))
    return render_template("admin/employee_form.html",departments=departments,employee=employee)


@admin_bp.route("/employees/<int:employee_id>/delete",methods=["POST"])
@login_required
@admin_required
def delete_employee(employee_id):
    employee=Employee.query.get_or_404(employee_id); db.session.delete(employee); db.session.delete(employee.user); db.session.commit()
    flash("Employee deleted.","info")
    return redirect(url_for("admin.employees"))


@admin_bp.route("/employee-details")
@login_required
@admin_required
def employee_details():
    search=request.args.get("search","").strip(); query=Employee.query
    if search:
        query=query.filter(db.or_(Employee.full_name.ilike(f"%{search}%"),Employee.employee_code.ilike(f"%{search}%"),Employee.designation.ilike(f"%{search}%")))
    data=[]
    for e in query.order_by(Employee.full_name).all():
        data.append({"employee":e,"salary_history":Salary.query.filter_by(employee_id=e.id).order_by(Salary.year.desc(),Salary.month.desc()).all(),"attendance_count":Attendance.query.filter_by(employee_id=e.id).count(),"leave_count":Leave.query.filter_by(employee_id=e.id).count()})
    return render_template("admin/employee_details.html",employee_data=data,search=search)


@admin_bp.route("/employee-details/<int:employee_id>")
@login_required
@admin_required
def employee_detail(employee_id):
    e=Employee.query.get_or_404(employee_id)
    return render_template("admin/employee_detail.html",employee=e,
        salary_history=Salary.query.filter_by(employee_id=e.id).order_by(Salary.year.desc(),Salary.month.desc()).all(),
        attendance_history=Attendance.query.filter_by(employee_id=e.id).order_by(Attendance.date.desc()).all(),
        leave_history=Leave.query.filter_by(employee_id=e.id).order_by(Leave.applied_on.desc()).all())


@admin_bp.route("/departments",methods=["GET","POST"])
@login_required
@admin_required
def departments():
    if request.method=="POST":
        f=request.form; name=f.get("name","").strip()
        if name and not Department.query.filter_by(name=name).first():
            db.session.add(Department(name=name,description=f.get("description","").strip())); db.session.commit(); flash("Department added.","success")
        else: flash("Department name is required and must be unique.","danger")
        return redirect(url_for("admin.departments"))
    return render_template("admin/departments.html",departments=Department.query.order_by(Department.name).all())


@admin_bp.route("/departments/<int:department_id>/delete",methods=["POST"])
@login_required
@admin_required
def delete_department(department_id):
    db.session.delete(Department.query.get_or_404(department_id)); db.session.commit(); flash("Department deleted.","info")
    return redirect(url_for("admin.departments"))


@admin_bp.route("/attendance")
@login_required
@admin_required
def attendance():
    selected_date=request.args.get("date") or date.today().isoformat()
    records=Attendance.query.filter_by(date=selected_date).join(Employee).order_by(Employee.full_name).all()
    marked={r.employee_id for r in records}; employees=Employee.query.order_by(Employee.full_name).all()
    return render_template("admin/attendance.html",records=records,unmarked=[e for e in employees if e.id not in marked],selected_date=selected_date)


@admin_bp.route("/attendance/mark",methods=["POST"])
@login_required
@admin_required
def mark_attendance():
    employee_id=request.form.get("employee_id"); status=request.form.get("status","present"); att_date=request.form.get("date") or date.today().isoformat()
    record=Attendance.query.filter_by(employee_id=employee_id,date=att_date).first()
    if record: record.status=status
    else: db.session.add(Attendance(employee_id=employee_id,date=att_date,status=status))
    db.session.commit(); flash("Attendance recorded.","success")
    return redirect(url_for("admin.attendance",date=att_date))


@admin_bp.route("/leaves")
@login_required
@admin_required
def leaves():
    status=request.args.get("status","pending"); query=Leave.query.join(Employee)
    if status!="all": query=query.filter(Leave.status==status)
    return render_template("admin/leaves.html",leaves=query.order_by(Leave.applied_on.desc()).all(),status_filter=status)


@admin_bp.route("/leaves/<int:leave_id>/<string:decision>",methods=["POST"])
@login_required
@admin_required
def decide_leave(leave_id,decision):
    if decision not in ("approved","rejected"):
        flash("Invalid decision.","danger"); return redirect(url_for("admin.leaves"))
    leave=Leave.query.get_or_404(leave_id); leave.status=decision; db.session.commit(); flash(f"Leave request {decision}.","success")
    return redirect(url_for("admin.leaves"))


@admin_bp.route("/salary/<int:employee_id>",methods=["GET","POST"])
@login_required
@admin_required
def salary(employee_id):
    employee=Employee.query.get_or_404(employee_id)
    if request.method=="POST":
        f=request.form; month=int(f.get("month")); year=int(f.get("year")); basic=float(f.get("basic",0)); allowances=float(f.get("allowances",0)); deductions=float(f.get("deductions",0))
        record=Salary.query.filter_by(employee_id=employee_id,month=month,year=year).first()
        if not record: record=Salary(employee_id=employee_id,month=month,year=year); db.session.add(record)
        record.basic=basic; record.allowances=allowances; record.deductions=deductions; record.net_salary=basic+allowances-deductions; record.paid_on=date.today()
        db.session.commit(); flash("Salary record saved.","success")
        return redirect(url_for("admin.salary",employee_id=employee_id))
    return render_template("admin/salary.html",employee=employee,records=Salary.query.filter_by(employee_id=employee_id).order_by(Salary.year.desc(),Salary.month.desc()).all())


@admin_bp.route("/reports")
@login_required
@admin_required
def reports():
    dept_counts=db.session.query(Department.name,db.func.count(Employee.id)).outerjoin(Employee).group_by(Department.name).all()
    leave_counts=db.session.query(Leave.status,db.func.count(Leave.id)).group_by(Leave.status).all()
    total_net_salary=db.session.query(db.func.coalesce(db.func.sum(Salary.net_salary),0)).scalar()
    return render_template("admin/reports.html",dept_counts=dept_counts,leave_counts=leave_counts,total_net_salary=total_net_salary)