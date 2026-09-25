# Employee Management System

A web-based Employee Management System built with **Python Flask and MySQL**.

The system provides separate dashboards and functionality for two roles:

- **Admin**
- **Employee**

It manages employee records, departments, attendance, leave requests, salary information, reports, and employee profiles through a clean web interface.

---

## Features

### Admin Module

- Admin login and authentication
- Admin dashboard
- Employee management
  - Add employees
  - Edit employee information
  - Delete employees
  - Search employees
  - Filter employees by department
- Department management
- Attendance management
  - View attendance
  - Mark attendance
  - Update attendance
  - Filter attendance by date
- Leave management
  - View leave requests
  - Approve leave
  - Reject leave
- Salary management
  - Add salary records
  - View salary information
- Reports & Analytics
  - Employees by department
  - Leave status distribution
  - Attendance status distribution
  - Monthly attendance
  - Total net salary
- Employee Details
  - View all employees
  - Open individual employee profiles
  - View personal information
  - View salary history
  - View attendance history
  - View leave history
- Dark mode

### Employee Module

- Employee login
- Employee dashboard
- View personal profile
- View department and designation
- View attendance history
- Mark attendance
- Apply for leave
- View leave status
- View salary information
- Dark mode

### Authentication & Security

- Login and logout
- Role-based access control
- Separate Admin and Employee permissions
- Password hashing
- Environment-based database configuration
- Protected admin and employee routes

---

## Technology Stack

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Jinja2 templates
- Font Awesome
- Chart.js

### Backend

- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy

### Database

- MySQL
- PyMySQL

---

## Project Structure

```text
ems/
│
├── app.py
├── config.py
├── extensions.py
├── models.py
├── seed.py
├── schema.sql
├── requirements.txt
├── README.md
├── .env.example
│
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── admin.py
│   ├── employee.py
│   └── utils.py
│
├── templates/
│   ├── base.html
│   │
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   │
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── employees.html
│   │   ├── employee_form.html
│   │   ├── employee_details.html
│   │   ├── employee_profile.html
│   │   ├── departments.html
│   │   ├── attendance.html
│   │   ├── leaves.html
│   │   ├── salary.html
│   │   └── reports.html
│   │
│   └── employee/
│       ├── dashboard.html
│       ├── profile.html
│       ├── attendance.html
│       ├── leave.html
│       └── salary.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    └── js/
        └── script.js