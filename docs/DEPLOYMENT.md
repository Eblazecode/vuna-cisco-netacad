# Deployment — GitHub, Supabase and Vercel

## Current architecture

- Django REST Framework remains the backend API and source of business rules.
- Supabase provides managed PostgreSQL. Keep the connection string server-side.
- Vercel hosts the React/TypeScript frontend when that application is introduced.
- Do not expose the Supabase database password, service-role key or Django secret to the browser.

## Supabase database

The project reference configured for this application is `amlykkrdayvujdznurat` (project URL: `https://amlykkrdayvujdznurat.supabase.co`). The project was found in the account but reported as inactive during initial integration checks. Restore it in the Supabase dashboard before applying migrations or connecting the API.

For Django's persistent database sessions, select the Supabase **Session pooler** connection string (port 5432) from Project > Connect. Add `?sslmode=require` if it is not already present. If the project network supports IPv6 or an IPv4 add-on is enabled, a direct connection may also be used. Do not use transaction pooler mode for Django's normal persistent ORM connections.

Set `DATABASE_URL` as an encrypted environment variable in the backend hosting environment. Never commit a real URL or password.

## Vercel

The existing Vercel project is `vuna-cisco-netacad`. Its current deployment is connected to the GitHub repository and reports READY, but the repository currently contains a Django API rather than a frontend application. Vercel is therefore not yet the production host for the Django API.

When `frontend/` is introduced:
1. Configure the Vercel project's Root Directory to `frontend`.
2. Use the framework preset matching the frontend (Vite or Next.js as selected by the frontend implementation).
3. Add only public client-side configuration to `VITE_*` or `NEXT_PUBLIC_*` variables.
4. Add a rewrite or server-side proxy for API calls to the separately hosted Django API.
5. Configure allowed origins and CSRF trusted origins on Django.

## Django API hosting

Deploy the Django container to an institution-approved container host. Configure:
- `DJANGO_SECRET_KEY` (unique random secret)
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `CORS_ALLOWED_ORIGINS`
- `DATABASE_URL` (Supabase Session Pooler, SSL)
- `REDIS_URL` (only when background workers are enabled)

Run committed Django migrations as a release step. Do not use `migrate --run-syncdb` as the production schema-management strategy.

## Readiness checks

- Restore the Supabase project and confirm database connectivity.
- Apply and verify committed migrations.
- Run Django system checks and full tests against PostgreSQL.
- Add Vercel frontend after the frontend project exists.
- Run role/scope tests, security review, backup/restore test and institutional UAT before student onboarding.
