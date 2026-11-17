# Deployment — GitHub, Supabase and Vercel

## Current architecture

- Django REST Framework remains the backend API and source of business rules.
- Supabase provides managed PostgreSQL. Keep the connection string server-side.
- Vercel hosts the React/TypeScript frontend and a separate Django API project.
- Do not expose the Supabase database password, service-role key or Django secret to the browser.

## Supabase database

The project reference configured for this application is `amlykkrdayvujdznurat` (project URL: `https://amlykkrdayvujdznurat.supabase.co`). A restore was requested for the existing project. Confirm the project reports `ACTIVE_HEALTHY` before applying migrations or connecting the API.

Copy the exact Supabase **Session pooler** connection string (port 5432) from Project > Connect. Replace the password placeholder, URL-encode reserved password characters, and include `?sslmode=require`. Do not construct the pooler hostname or username manually.

Set `DATABASE_URL` as an encrypted environment variable in the backend hosting environment. Never commit a real URL or password.

## Vercel

Two Vercel projects are connected to this GitHub repository:

1. `vuna-cisco-netacad` — Root Directory `frontend`, framework Vite.
2. `vuna-cisco-netacad-api` — repository root, Django framework/runtime.

Vercel's Django support detects `manage.py` and discovers the WSGI/ASGI entry point from Django settings. The frontend and API are built and deployed independently. The frontend uses `VITE_API_BASE_URL` to reach the API. Configure CORS and CSRF trusted origins to the exact frontend HTTPS origins.

## Django API hosting

Deploy the Django API through the `vuna-cisco-netacad-api` Vercel project. Configure:
- `DJANGO_SECRET_KEY` (unique random secret)
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `CORS_ALLOWED_ORIGINS`
- `DATABASE_URL` (Supabase Session Pooler, SSL)
- `REDIS_URL` (only when background workers are enabled)

Run committed Django migrations as a release step. Do not use `migrate --run-syncdb` as the production schema-management strategy.

The Django settings reject non-debug deployments without `DATABASE_URL`; this prevents accidental production use of ephemeral SQLite.

## Readiness checks

- Restore the Supabase project and confirm database connectivity.
- Apply and verify committed migrations.
- Run Django system checks and full tests against PostgreSQL.
- Set `VITE_API_BASE_URL` in the frontend Vercel project after the API has a verified HTTPS origin.
- Run role/scope tests, security review, backup/restore test and institutional UAT before student onboarding.
