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
