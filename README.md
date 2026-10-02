# Employee Management System

A Flask + MySQL web app for managing employees, departments, attendance, leave requests, salaries, resumes, and offer letters.

## Roles

- **Admin** — Full system management
- **HR** — Employee information, attendance, leave requests, resumes, and offer letters
- **Employee** — Own profile, attendance, leave, and salary

## Stack

- **Frontend:** HTML, Bootstrap 5, Jinja, vanilla JavaScript
- **Backend:** Python, Flask, Flask-Login, Flask-SQLAlchemy
- **Database:** MySQL with PyMySQL

## Project Structure

```text
ems/
├── app.py
├── config.py
├── extensions.py
├── models.py
├── seed.py
├── schema.sql
├── requirements.txt
├── routes/
│   ├── auth.py
│   ├── admin.py
│   ├── employee.py
│   ├── hr.py
│   └── utils.py
├── templates/
├── static/
├── Stored Data/
│   ├── Resumes/
│   └── Offer Letters/
└── .env