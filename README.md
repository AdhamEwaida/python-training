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
