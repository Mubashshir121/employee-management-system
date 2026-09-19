from datetime import date, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="employee")  # admin | employee
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship(
        "Employee", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def is_admin(self):
        return self.role == "admin"


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))

    employees = db.relationship("Employee", back_populates="department")


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    designation = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    date_joined = db.Column(db.Date, default=date.today)

    user = db.relationship("User", back_populates="employee")
    department = db.relationship("Department", back_populates="employees")
    attendance_records = db.relationship(
        "Attendance", back_populates="employee", cascade="all, delete-orphan"
    )
    leaves = db.relationship("Leave", back_populates="employee", cascade="all, delete-orphan")
    salary_records = db.relationship(
        "Salary", back_populates="employee", cascade="all, delete-orphan"
    )


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False, default="present")  # present|absent|leave
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)

    employee = db.relationship("Employee", back_populates="attendance_records")

    __table_args__ = (db.UniqueConstraint("employee_id", "date", name="uq_employee_date"),)


class Leave(db.Model):
    __tablename__ = "leaves"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending|approved|rejected
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship("Employee", back_populates="leaves")


class Salary(db.Model):
    __tablename__ = "salary"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    basic = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    allowances = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    deductions = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    net_salary = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    paid_on = db.Column(db.Date)

    employee = db.relationship("Employee", back_populates="salary_records")

    __table_args__ = (db.UniqueConstraint("employee_id", "month", "year", name="uq_employee_month_year"),)
