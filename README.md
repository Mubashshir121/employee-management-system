# Employee Management System

Flask + MySQL web app with two roles — **Admin** and **Employee** — covering
employee records, departments, attendance, leave, and salary.

## Stack

- Frontend: HTML, Bootstrap 5, vanilla JS (server-rendered with Jinja)
- Backend: Python, Flask, Flask-Login, Flask-SQLAlchemy
- Database: MySQL (via PyMySQL)

## Project structure

```
ems/
├── app.py              # app factory + entry point
├── config.py           # reads DB settings from environment variables
├── extensions.py       # db, login_manager singletons
├── models.py           # 6 tables: users, employees, departments,
│                        #   attendance, leaves, salary
├── seed.py             # creates tables + one admin login + a department
├── schema.sql           # same 6 tables as raw SQL, if you'd rather run it by hand
├── routes/
│   ├── auth.py          # login, self-registration, logout
│   ├── admin.py         # admin module: employees, departments, attendance,
│   │                     #   leave approval, salary, reports
│   ├── employee.py       # employee module: profile, attendance, leave, salary
│   └── utils.py          # @admin_required / @employee_required decorators
├── templates/            # Jinja + Bootstrap templates
└── static/                # custom CSS/JS
```

## Setup

1. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create the MySQL database.** Either let SQLAlchemy create the tables
   (step 4) after you create an empty schema:

   ```sql
   CREATE DATABASE employee_management CHARACTER SET utf8mb4;
   ```

   or run `schema.sql` directly in MySQL Workbench / the `mysql` CLI, which
   creates the database and all 6 tables in one go.

3. **Configure environment variables.** Copy `.env.example` to `.env` and
   fill in your MySQL credentials (or just export them in your shell):

   ```bash
   cp .env.example .env
   ```

   `config.py` reads `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`,
   and `SECRET_KEY`. If you skip this, it falls back to
   `root` / `password` / `localhost` / `3306` / `employee_management`.

4. **Create tables and seed an admin account:**

   ```bash
   python seed.py
   ```

   This prints the admin login: `admin` / `admin123`. Change that password
   once you're using this for real.

5. **Run the app:**

   ```bash
   flask --app app run --debug
   ```

   Visit `http://127.0.0.1:5000`. Log in as `admin` to see the admin
   dashboard, or register a new employee account from the login page.

## How the modules map to routes

| Module | Route prefix | Highlights |
|---|---|---|
| Admin | `/admin` | employees CRUD, departments, mark/view attendance, approve/reject leave, salary entry, reports |
| Employee | `/employee` | profile, view department, mark/view own attendance, apply for leave + view status, view salary |
| Auth | `/` | login, self-registration (creates an employee account), logout |

## Notes on the schema

Six tables, matching the ER flow in the brief:

- `users` — login credentials + role (`admin` or `employee`)
- `employees` — 1:1 with `users`, holds personal/work details, FK to `departments`
- `departments` — 1:M to `employees`
- `attendance` — 1:M from `employees`, one row per employee per date
- `leaves` — 1:M from `employees`, tracks status (`pending`/`approved`/`rejected`)
- `salary` — 1:M from `employees`, one row per employee per month/year

Everything here is a functional starting point, not a hardened production
build — before deploying anywhere real you'd want CSRF protection
(Flask-WTF), stronger password policy, input validation, and HTTPS.
