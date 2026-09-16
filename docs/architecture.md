# TutorSetu Phase 1 Architecture

## Scope

Phase 1 establishes a secure foundation. Phase 2 adds authentication, password
security, email verification, JWT revocation, and application-role permissions.
Tutor registration, marketplace workflows, messaging, payments, recommendations,
and mobile clients remain out of scope.

## Components

- **Frontend:** React 18 + Vite, served from `frontend/`.
- **Backend:** Django 5 + Django REST Framework, served from `backend/`.
- **Database:** PostgreSQL, configured entirely through environment variables.
- **API boundary:** The frontend uses the centralized Axios client in
  `frontend/src/api/axios.js`.
- **Navigation:** React Router provides the Phase 1 routes. The route pages are
  placeholders only and do not implement authentication or marketplace workflows.

## Request flow

The browser loads the React application from Vite. React calls the Django REST API
through the configured API base URL. Django applies restricted CORS rules and
returns JSON responses. Persistent domain models will be introduced in later phases.

## Security baseline

- Secrets are loaded from `.env` and are never committed.
- Django debug mode defaults to disabled.
- CORS origins are explicitly configured.
- Production deployment must provide a strong secret key, allowed hosts, trusted
  origins, HTTPS, and managed PostgreSQL credentials.
- Passwords use Django's PBKDF2 hasher and configured validators.
- Password reset responses are intentionally generic to prevent account
  enumeration.
- Email verification is represented by `User.email_verified`; no marketplace
  endpoint is enabled until later phases.
