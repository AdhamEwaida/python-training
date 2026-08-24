# Python Training

This repository contains my Python practical training exercises.

## Week 1 – Python Foundations

### Day 1
- Python environment setup
- Virtual environment (venv)
- Git & GitHub
- Black formatter
- Flake8 linter
- CLI program using `sys.argv`

### Day 2
- Control flow and input validation
- BMI calculator with type hints
- Unit tests for valid and invalid inputs using pytest

Run the Day 2 tests with:

```powershell
python -m pytest
```

### Day 3
- Student grade storage and validation
- Top-three ranking using `sorted` and a lambda expression
- Pass/fail transformation using a dictionary comprehension
- Pytest coverage for sorting, transformations, and invalid data

Run the grade report with:

```powershell
python grades.py
```

### Day 4
- In-memory command-line contact book using a dictionary of dictionaries
- Case-insensitive O(1) average name lookup with `dict.get`
- O(n) phone-number search using iteration
- Sorted contact listing and defensive copies
- Set union and intersection for comparing contact-book names

Run the contact book with:

```powershell
python contact_book.py
```

#### Complexity analysis

| Operation | Time complexity | Reason |
|---|---:|---|
| Add contact | O(1) average | Dictionary insertion by normalized name |
| Search by name | O(1) average | Direct dictionary lookup with `dict.get` |
| Search by phone | O(n) | Contacts may all need to be scanned |
| List contacts alphabetically | O(n log n) | Contacts are sorted by name |
| Name-set union | O(n + m) | Both sets must be combined |
| Name-set intersection | O(min(n, m)) average | Membership checks use hash sets |

### Day 5
- Refactored the contact book into a `contacts` package
- Added validated JSON persistence in `contacts.json`
- Added custom storage exceptions and CLI error handling
- Added password-strength validation with `WeakPasswordError`
- Added pytest coverage for persistence, corrupt data, CLI saving, and passwords

Run the persistent contact book with:

```powershell
python contact_book.py
```

The contact package is organized as follows:

```text
contacts/
├── __init__.py
├── manager.py
└── utils.py
```

A strong password must contain at least eight characters, one uppercase letter,
one number, and one special character. Invalid passwords raise
`WeakPasswordError`.

### Day 6
- Built a command-line student management system
- Added student registration and grade updates with validation
- Added average calculation and top-student ranking
- Added JSON and CSV exports
- Added pytest coverage for valid and invalid cases

Run the project with:

```powershell
python student_manager.py
```

Run all tests with:

```powershell
python -m pytest
```

## Week 2 – Advanced Python and Flask Foundations

### Day 7
- Added an object-oriented `Student` class with name, student ID, and grades
- Used the shared class variable `school_name` to demonstrate class state
- Added `add_grade()` and `get_average()` instance methods
- Added readable `__str__()` and developer-focused `__repr__()` representations
- Added pytest coverage for construction, independent instance state, validation,
  averages, and string representations

Try the class interactively with:

```powershell
python -c "from student import Student; print(Student('Adham', 'S1', [90, 80]))"
```

### Day 8
- Extended `Student` with `GraduateStudent` using inheritance and `super()`
- Overrode `__str__()` and `__repr__()` to include a thesis title
- Added a `Professor` class that assigns validated grades to students
- Added a `Course` class that contains student objects through composition
- Demonstrated protected attributes with `_department` and `_thesis_title`
- Demonstrated a private attribute with `Professor.__employee_id`
- Added pytest coverage for inheritance, overriding, encapsulation, and composition

Inheritance is used when one class **is a** specialized form of another class:
`GraduateStudent` is a `Student`. Composition is used when one object **has**
other objects: a `Course` has enrolled `Student` objects.

Try the Day 8 classes interactively with:

```powershell
python -c "from course import Course; from student import GraduateStudent; c = Course('CS301', 'Advanced Python'); c.add_student(GraduateStudent('Adham', 'G1', 'Flask APIs')); print(c)"
```

### Day 9
- Added the automatically calculated `Student.gpa` property
- Added student equality comparison based on case-insensitive student IDs
- Made `Course` iterable while preserving enrollment order
- Added `len(course)` support through `__len__()`
- Added `Student.set_school_name()` as a class-method example
- Added a validated `GraduateStudent.thesis_title` property setter
- Extended pytest coverage for properties, equality, iteration, and class methods

Iterate over a course and inspect each student's calculated GPA with:

```powershell
python -c "from course import Course; from student import Student; c = Course('CS301', 'Advanced Python'); c.add_student(Student('Adham', 'S1', [90, 80])); print([(s.name, s.gpa) for s in c])"
```

### Day 10
- Refactored the object-oriented student system into a `school` package
- Added a single public package interface for `Student`, `GraduateStudent`,
  `Course`, and `Professor`
- Kept the original top-level modules as compatibility imports
- Added pinned development dependencies in `requirements.txt`
- Added pytest coverage for package imports and compatibility

The package is organized as follows:

```text
school/
├── __init__.py
├── course.py
├── professor.py
└── student.py
```

Install the project tools with:

```powershell
python -m pip install -r requirements.txt
```

Import the models from the package's public interface:

```powershell
python -c "from school import Course, Student; c = Course('CS301', 'Advanced Python'); c.add_student(Student('Adham', 'S1', [90, 80])); print(c)"
```

### Day 11
- Added a lightweight Flask application in `app.py`
- Added a welcome route at `GET /`
- Added a dynamic greeting route at `GET /hello/<name>`
- Restricted both routes to GET requests and safely escaped URL input
- Added Flask test-client coverage for successful responses, HTML escaping, and
  rejected POST requests

Install the dependencies and run the development server with:

```powershell
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

Then open `http://127.0.0.1:5000/` or
`http://127.0.0.1:5000/hello/Adham` in a browser.

### Day 12
- Replaced inline HTML responses with reusable Jinja templates
- Added template inheritance and navigation through `templates/base.html`
- Added a student registration form handled with GET and POST requests
- Added server-side validation for names, emails, and courses
- Stored registered students in an in-memory Python list
- Added a student-list template using Jinja loops and conditions
- Extended Flask test-client coverage for forms, validation, redirects, empty
  states, and automatic HTML escaping

Available pages:

- `GET /` — homepage
- `GET /hello/<name>` — dynamic greeting
- `GET /students` — registered student list
- `GET /students/register` — registration form
- `POST /students/register` — process a registration

Data is stored in memory and resets whenever the Flask development server is
restarted.

### Day 13
- Completed the Flask Student Portal v1 challenge
- Split student storage and form validation into the `student_portal` package
- Added stable numeric IDs for in-memory student records
- Added optional comma-separated grades with server-side validation
- Added individual student detail pages with grades and calculated averages
- Linked every student in the list to their detail page
- Extended Flask test-client coverage for registration, validation, detail
  pages, list links, and missing students

The portal structure is:

```text
student_portal/
├── __init__.py
├── store.py
└── validation.py
templates/
├── base.html
├── index.html
├── register.html
├── student_detail.html
└── students.html
```

Available project routes:

- `GET /` — homepage and navigation
- `GET /students` — registered student list
- `GET /students/register` — registration form
- `POST /students/register` — validate and register a student
- `GET /students/<student_id>` — individual details and grades

Run the portal with:

```powershell
python -m flask --app app run --debug
```

### Day 19

- Began the capstone by completing HTML and REST CRUD for courses
- Added validation and conflict handling for course names and enrolled courses
- Added student search across names, emails, and course names
- Added server-side pagination to the student directory
- Added focused capstone tests for course workflows and search

Course API endpoints:

- `GET /api/courses`
- `POST /api/courses`
- `GET /api/courses/<course_id>`
- `PUT /api/courses/<course_id>`
- `DELETE /api/courses/<course_id>`

### Day 20

- Completed the Week 3 capstone requirements across `User`, `Student`, and
  `Course` models
- Added REST CRUD for user accounts with password hashing and safe serialization
- Kept authentication secrets out of every API response
- Added validation, case-insensitive duplicate detection, and JSON 404 responses
- Documented the final resource endpoints and verification commands

User API endpoints:

- `GET /api/users`
- `POST /api/users`
- `GET /api/users/<user_id>`
- `PUT /api/users/<user_id>`
- `DELETE /api/users/<user_id>`

Verify the complete project before delivery:

```powershell
python -m pytest -q
python -m black --check .
python -m flake8 .
```

### Day 21

- Reviewed the capstone architecture and defined the Pro Edition milestones
- Documented the daily-delivery and production branch strategies
- Added a DBML schema for users, students, courses, and enrollments
- Added a concise API specification with current and planned endpoints
- Recorded security, compatibility, migration, and deletion decisions

Planning documents:

- [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md)
- [`docs/schema.dbml`](docs/schema.dbml)
- [`docs/API.md`](docs/API.md)

### Day 22

- Added an explicit `Enrollment` model with a unique student-course constraint
- Added many-to-many enrollment list, create, and delete API endpoints
- Added searchable, paginated course lists in HTML and JSON
- Added a repeatable `flask seed` command that creates demo enrollments
- Added an Alembic migration and relationship-focused tests

Initialize and seed a local database with:

```powershell
python -m flask --app app db upgrade
python -m flask --app app seed
```

### Day 23

- Added session-backed CSRF protection for every server-rendered write form
- Added validated student profile-picture uploads with generated filenames
- Added custom HTML pages for 404 and 500 responses
- Added user roles and profile-picture metadata to the database schema
- Added an Alembic migration, upload exclusions, and advanced Flask tests

Uploaded images are limited to 2 MiB and stored under the ignored `instance/`
directory. Configure another location with `UPLOAD_FOLDER` when needed.

### Day 24

- Added API contract tests for students, courses, and users
- Added a mocked database-outage test that verifies JSON errors and rollback
- Added branch-aware coverage configuration with an enforced 80% minimum
- Added a GitHub Actions workflow for Python 3.12 and 3.13
- Added automated Black, Flake8, test, and coverage checks on every push

Run the same verification used by CI with:

```powershell
python -m black --check .
python -m flake8 .
python -m pytest --cov --cov-report=term-missing --cov-report=xml
```

The coverage threshold is configured in `.coveragerc`. CI fails whenever total
coverage drops below 80%, and the Python 3.13 job uploads `coverage.xml` as a
workflow artifact.

### Day 14
- Replaced the in-memory student list with a persistent SQLite database
- Added SQLAlchemy `Student` and `Course` models with a one-to-many relationship
- Added Flask-Migrate and an initial migration for both database tables
- Kept student creation and detail pages backed by database queries
- Added student update and delete routes to complete CRUD operations
- Added a course list with enrollment counts
- Added an idempotent `seed.py` script with demo courses and students
- Reworked Flask tests to use a fresh in-memory SQLite database

Prepare and run the database-backed portal with:

```powershell
python -m pip install -r requirements.txt
python -m flask --app app db upgrade
python seed.py
python -m flask --app app run --debug
```

Database-related pages and actions:

- `GET /students` — list students from SQLite
- `POST /students/register` — create a student and course when needed
- `GET /students/<student_id>` — read one student
- `GET|POST /students/<student_id>/edit` — update one student
- `POST /students/<student_id>/delete` — delete one student
- `GET /courses` — list courses and enrollment counts

The seed script is safe to run more than once; existing demo records are reused.

### Day 15
- Introduced the `create_app()` application factory in `student_portal`
- Moved default settings into a dedicated `Config` class
- Split routes into `main`, `students`, and `courses` blueprints
- Grouped student and course URLs with blueprint URL prefixes
- Moved Jinja templates inside the application package
- Kept `app.py` as a small Flask CLI and development-server entry point
- Updated tests to create a fresh application instance for every test

The application package is now organized as follows:

```text
student_portal/
|-- __init__.py
|-- config.py
|-- database.py
|-- models.py
|-- validation.py
|-- routes/
|   |-- __init__.py
|   |-- main.py
|   |-- students.py
|   `-- courses.py
`-- templates/
    |-- base.html
    |-- courses.html
    |-- hello.html
    |-- index.html
    |-- register.html
    |-- student_detail.html
    `-- students.html
```

The application factory accepts configuration overrides, which keeps testing
isolated while the normal Flask commands continue to work through `app.py`:

```powershell
python -m flask --app app db upgrade
python -m flask --app app run --debug
```

### Day 16
- Added a JSON REST API in a dedicated `api` blueprint
- Added endpoints to list, create, read, update, and delete students
- Added JSON payload validation for required fields and numeric grades
- Added consistent JSON errors for validation, missing records, and database errors
- Reused case-insensitive course and email queries across HTML and API routes
- Added automated API tests for success and failure responses
- Added an importable Postman collection in `postman/`

Available API endpoints:

| Method | Endpoint | Result |
| --- | --- | --- |
| `GET` | `/api/students` | List all students |
| `POST` | `/api/students` | Create a student |
| `GET` | `/api/students/<student_id>` | Read one student |
| `PUT` | `/api/students/<student_id>` | Replace student fields |
| `DELETE` | `/api/students/<student_id>` | Delete a student |

Example request body for `POST` and `PUT`:

```json
{
  "name": "Adham",
  "email": "adham@example.com",
  "course": "Python",
  "grades": [90, 85, 80]
}
```

Start the server, then import
`postman/Student Portal API.postman_collection.json` into Postman. Run **Create
Student** first; its test script automatically saves the returned ID for the
read, update, and delete requests.

### Day 17
- Added database-backed user accounts with securely hashed passwords
- Integrated Flask-Login session management and a database user loader
- Added account registration, login, and logout routes with flash feedback
- Added a protected dashboard that redirects anonymous visitors to login
- Updated navigation to reflect whether a user is signed in
- Added automated authentication and session tests

Authentication routes:

| Method | Endpoint | Result |
| --- | --- | --- |
| `GET|POST` | `/register` | Create a portal account |
| `GET|POST` | `/login` | Start an authenticated session |
| `POST` | `/logout` | End the current session |
| `GET` | `/dashboard` | View the protected dashboard |

Apply the new user-table migration before trying authentication:

```powershell
python -m pip install -r requirements.txt
python -m flask --app app db upgrade
python -m flask --app app run --debug
```

### Day 18
- Added `.env` loading with `python-dotenv` for local configuration
- Added separate development and production settings selected by `APP_ENV`
- Read the secret key and database URL from runtime environment variables
- Rejected the insecure default secret key when production mode starts
- Enabled secure, HTTP-only session cookie defaults for production
- Added a production WSGI entry point and Gunicorn dependency
- Added automated tests for configuration selection and validation

Create local settings without committing secrets:

```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Put the generated value in `.env`, then start the development server:

```powershell
python -m flask --app app run --debug
```

For production, configure the variables on the hosting platform and start the
WSGI application with:

```text
APP_ENV=production
SECRET_KEY=<strong-random-value>
DATABASE_URL=<production-database-url>
```

```bash
gunicorn wsgi:app
```

Gunicorn runs on Linux deployment environments. On Windows, continue using the
Flask development server locally or run Gunicorn through WSL.
