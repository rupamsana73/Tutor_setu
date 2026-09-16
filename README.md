# TutorSetu

Secure, startup-oriented tutor marketplace foundation.

## Phase 1 status

This repository currently contains **Phase 1: Secure Foundation & Architecture**:

- React + Vite frontend
- Django + Django REST Framework backend
- PostgreSQL configuration
- Restricted CORS and secure environment-based settings
- Centralized Axios API client
- `GET /api/health/` endpoint
- Responsive TutorSetu landing page
- React Router foundation routes: `/`, `/find-tutors`, `/become-tutor`,
  `/how-it-works`, `/about`, `/login`, and `/register`
- Architecture, API, and database documentation

Marketplace features such as authentication, tutor registration, enquiries,
reviews, chat, payments, recommendations, maps, and mobile clients are intentionally
out of scope for this phase.

## Project structure

```text
backend/      Django project and REST API
frontend/     React + Vite application
docs/         Architecture, API, and database documentation
```

## Local setup

### Backend

1. Create and activate a virtual environment:

   ```powershell
   cd backend
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Copy `backend/.env.example` to `backend/.env` and fill in local values.
   `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD` must not be committed.

4. Start Django:

   ```powershell
   py manage.py runserver
   ```

The API health endpoint is available at
`http://localhost:8000/api/health/`.

### Frontend

1. Install Node.js dependencies:

   ```powershell
   cd frontend
   npm install
   ```

2. Copy `frontend/.env.example` to `frontend/.env`.

3. Start Vite:

   ```powershell
   npm run dev
   ```

The landing page is available at `http://localhost:5173/`.

## Security rules

- Never commit `.env`, credentials, virtual environments, `node_modules`, or
  generated build files.
- Never enable `CORS_ALLOW_ALL_ORIGINS` as a permanent setting.
- Keep `DJANGO_DEBUG=False` outside local development.
- Use a managed PostgreSQL instance and secret store for production.
