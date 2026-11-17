# VUNA Cisco NetAcad — Web Portal

React + TypeScript + Vite frontend for the Veritas University student and Cisco Networking Academy management platform.

## Local development

```bash
npm install
cp .env.example .env.local
npm run dev
```

Set `VITE_API_BASE_URL` to the base URL of the Django REST API. The frontend expects the API endpoints documented in the repository root README.

## Vercel

The Vercel project is configured to use this directory as its Root Directory.

- Framework preset: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Install command: `npm install`
- Environment variable: `VITE_API_BASE_URL`

The portal deliberately shows unavailable indicators when the API is not configured or reachable. It does not substitute invented student counts or operational statistics.

## Authentication

The current API uses Django REST Framework Simple JWT. Tokens are held in the browser tab's session storage for this initial build. Production hardening should move token handling to a backend-for-frontend with secure HttpOnly cookies where feasible, and enforce MFA for privileged staff accounts.

## Registration

The public registration form consumes the restricted public academic reference endpoint:
`GET /api/v1/public/academic-structure/`

Applications are submitted to:
`POST /api/v1/registration/`

Self-registered students remain pending verification and cannot sign in until approved by an authorised administrator.
