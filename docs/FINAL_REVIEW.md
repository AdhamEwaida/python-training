# Final Review Checklist

Use this checklist before sharing a release of the Student Management Dashboard
or after changing its deployment configuration.

## Local quality checks

From the repository root, install the pinned dependencies and run the same
checks enforced by GitHub Actions:

```powershell
python -m pip install -r requirements.txt
python -m black --check .
python -m flake8 .
python -m pytest --cov --cov-report=term-missing --cov-report=xml
```

The coverage configuration requires at least 80% total coverage. Do not commit
`coverage.xml`, `.coverage`, `.pytest_cache`, `.env`, or files in `instance/`.

## Database smoke test

Use a disposable local database when verifying a schema change:

```powershell
Copy-Item .env.example .env
python -m flask --app app db upgrade
python -m flask --app app seed
python -m flask --app app run --debug
```

Confirm that the home page, student directory, course directory, registration,
login, dashboard, and API remain available. The seed command is idempotent, so
it may be rerun without duplicating its demo records.

## Live deployment checks

The deployed application is available at
<https://python-training-student-portal.onrender.com>. On Render's free plan,
the first request after inactivity can take about a minute.

1. Open `/health` and confirm it returns HTTP 200 with `status` set to `ok`.
2. Confirm the Render event is marked **Live** and its commit matches the latest
   CI-verified commit on `main`.
3. Create a temporary account, sign in, and verify the protected dashboard.
4. Create a course and student, then confirm the record remains after a refresh.
5. Review service logs for migration, database, or upload failures.

The Render-managed `SECRET_KEY` and `DATABASE_URL` must remain platform
environment variables; neither belongs in the repository or screenshots.
