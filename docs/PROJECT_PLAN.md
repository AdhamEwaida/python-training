# Student Management Dashboard — Pro Edition

## Product goal

Turn the Week 3 capstone into a maintainable portal for administrators,
instructors, and students. The Pro Edition keeps the Flask application factory
and blueprint architecture while extending data relationships, discovery,
security, uploads, and automated delivery.

## Current architecture

- `student_portal/__init__.py` owns application construction and extension setup.
- `student_portal/models.py` owns the SQLAlchemy domain models.
- `student_portal/routes/` separates HTML, authentication, and JSON API concerns.
- `student_portal/services.py` contains reusable database queries.
- `student_portal/validation.py` validates browser and API input.
- `migrations/` records every production schema change.
- `tests/` exercises isolated in-memory application instances.

## Planned milestones

1. **Relationships and discovery**
   - Add explicit course enrollments.
   - Add course and enrollment APIs.
   - Filter and paginate students and courses.
   - Add a repeatable Flask CLI seed command.
2. **Secure forms and media**
   - Add CSRF-protected forms.
   - Upload validated student profile images.
   - Add custom HTML error pages and consistent flash feedback.
3. **Quality and delivery**
   - Keep coverage above 80%.
   - Run tests, Black, and Flake8 in GitHub Actions.
   - Document production environment configuration.
4. **User experience**
   - Improve navigation and responsive styling.
   - Add dashboard summaries and useful empty states.
5. **Final review**
   - Run migration and deployment smoke tests.
   - Audit documentation and endpoint behavior.

## Branch strategy

Normal feature work uses short-lived `feature/*` branches merged into `dev`.
Verified milestone releases merge from `dev` into `main`. The current training
delivery intentionally commits each requested day directly to `main` so the
history matches the daily submission requirement.

## Design decisions

- Database migrations are required for persistent schema changes.
- API responses never expose password hashes or local upload paths.
- Existing primary-course behavior stays compatible while explicit enrollments
  introduce the many-to-many relationship incrementally.
- Destructive course operations reject records with dependent students or
  enrollments instead of silently deleting related learning history.
- Uploads use generated filenames and extension allowlists; user-supplied paths
  are never trusted.
