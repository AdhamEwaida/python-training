# Deployment Guide

The repository includes a Render Blueprint in `render.yaml`. It provisions a
Python web service and a managed PostgreSQL database, generates the Flask
secret, runs Alembic migrations, starts Gunicorn, and monitors `/health`.

## Deploy with Render

1. Push the repository to GitHub.
2. Open the repository's **Deploy to Render** link in `README.md`.
3. Review the `python-training-student-portal` service and
   `python-training-db` database defined by the Blueprint.
4. Choose **Apply**. Render generates `SECRET_KEY` and injects the database
   connection string as `DATABASE_URL`.
5. Wait for the build, migration, and Gunicorn startup to finish.
6. Visit `/health`; a successful deployment returns:

   ```json
   {"environment": "production", "status": "ok"}
   ```

The free plans are suitable for training and demonstrations. Review Render's
current pricing and retention limits before using them for important data.

Official references:

- [Deploy a Flask app](https://render.com/docs/deploy-flask)
- [Blueprint YAML reference](https://render.com/docs/blueprint-spec)
- [Environment variables and secrets](https://render.com/docs/configure-environment-variables)

## Required environment variables

| Variable | Production value |
| --- | --- |
| `APP_ENV` | `production` |
| `SECRET_KEY` | A generated random secret; never commit it |
| `DATABASE_URL` | Render PostgreSQL connection string |

The application also supports SQLite for local development. Copy `.env.example`
to `.env`, replace the secret, and keep the file untracked.

## Manual platform configuration

On another Python hosting platform, use:

- Build command: `pip install -r requirements.txt`
- Release/migration command: `python -m flask --app app db upgrade`
- Start command: `gunicorn wsgi:app`
- Health-check path: `/health`

The platform must persist `DATABASE_URL` and support PostgreSQL. The
`psycopg[binary]` dependency provides the production database driver.

## Post-deployment checks

1. Confirm `/health` returns HTTP `200`.
2. Open `/register`, create a test account, and sign in.
3. Create a course and student, then verify they remain after a redeploy.
4. Check that production cookies include the `Secure` and `HttpOnly` flags.
5. Review service logs for migration, database, or upload errors.
