# VUNA Cisco NetAcad 2.0 — Backend foundation

A clean Django REST Framework implementation baseline for the Veritas University Student Management and Cisco Networking Academy Management System. This repository is being rebuilt against the approved SRS; it is not a continuation of the earlier Floot prototype.

## Architecture decisions

- **Pattern:** API-first modular monolith.
- **Backend:** Python 3.12+, Django 5.2, Django REST Framework.
- **Database:** PostgreSQL 17.
- **Authentication:** Custom email-based Django user, short-lived JWT access tokens and rotating refresh tokens.
- **Background work:** Celery + Redis (configured; task modules are added with the relevant feature phases).
- **API documentation:** OpenAPI schema and Swagger UI via drf-spectacular.
- **Deployment baseline:** Container-ready; production deployment target to be selected after institutional infrastructure/security review.

## Current implementation status

This initial engineering increment establishes the foundation and the first vertical slice:

- All 11 SRS user categories represented as explicit role values.
- Custom user model, email login, privileged account flags, faculty/department scope fields.
- Faculty, department, academic programme and academic session entities.
- Student profile with unique matriculation number and faculty/department/programme integrity checks.
- Self-service registration creates a **pending** student and inactive account; it does not grant access before verification.
- Student search/filter/list/retrieve/update endpoints for permitted academy/faculty/department administrators.
- Student approval/rejection/suspension status workflow and append-only application audit records.
- CSV student export.
- JWT login/refresh, authenticated `/me/`, admin user provisioning, API schema/docs.
- PostgreSQL/Redis local environment, Docker Compose, CI workflow and starter tests.

The full SRS contains 18 functional requirement groups. The remaining modules are intentionally not represented as complete merely because their architecture is planned. See `docs/IMPLEMENTATION-PLAN.md` for delivery sequencing and acceptance gates.

## Quick start (Docker)

```bash
cp .env.example .env
# Set DJANGO_SECRET_KEY to a unique random value before use.
docker compose up --build -d
# Create the first superuser
docker compose exec api python manage.py createsuperuser
```

API base URL: `http://localhost:8000/api/v1/`  
Swagger: `http://localhost:8000/api/docs/`  
Django admin: `http://localhost:8000/admin/`

## Quick start (local Python)

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Start PostgreSQL and Redis, then configure DATABASE_URL and REDIS_URL in .env.
python manage.py check
python manage.py makemigrations accounts academics students audit
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Initial API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/auth/token/` | Obtain JWT pair using email/password |
| POST | `/api/v1/auth/token/refresh/` | Rotate/refresh token |
| GET | `/api/v1/auth/me/` | Current authenticated user |
| GET/POST | `/api/v1/auth/users/` | Privileged user provisioning |
| POST | `/api/v1/registration/` | Public student self-registration (throttled) |
| GET/POST | `/api/v1/faculties/` | Faculty management |
| GET/POST | `/api/v1/departments/` | Department management |
| GET/POST | `/api/v1/academic-programmes/` | Programme management |
| GET/POST | `/api/v1/academic-sessions/` | Session management |
| GET/POST/PATCH | `/api/v1/students/` | Student directory and permitted record management |
| POST | `/api/v1/students/{id}/status/` | Approve/reject/suspend/activate workflow |
| GET | `/api/v1/students/export.csv/` | CSV export |

All management endpoints require an authenticated, authorised account. The initial implementation must receive a full security review before production use. In particular, institution-specific faculty/department assignment provisioning, MFA enforcement, malware scanning for uploads, and advanced scope policy tests are required before go-live.

## Important operating rules

1. A university student record is not the same as a training-course enrolment.
2. Self-registration is pending until verified by an authorised officer.
3. The portal does not replace the official Veritas University SIS, admissions/examination systems, or Cisco's learning platform.
4. Payment confirmation must be verified server-side and via signed provider webhook; a browser redirect is not proof of payment.
5. Dashboard statistics must be calculated from verified database records, never fabricated demo metrics.
6. Do not publish Cisco programme names/certification mappings until validated against the current authorised Cisco Networking Academy catalogue.
7. Do not place real student data, secrets, payment credentials or production database dumps in Git.

## Security note

The project is a development baseline, not a production-certified system. Use a strong secret, HTTPS, managed PostgreSQL with encrypted backups, restricted staff accounts, MFA for privileged roles, secure object storage, audit retention, tested recovery, and an institutional privacy impact assessment before onboarding real students.

**Migration generation note:** This source snapshot does not contain generated Django migration files yet. After installing dependencies, run `python manage.py makemigrations accounts academics students audit` and commit the generated migration files, then use `python manage.py migrate`. Do not rely on `--run-syncdb` for a production release.
