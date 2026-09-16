# TutorSetu Phase 1 API

## Health check

`GET /api/health/`

Example response:

```json
{
  "status": "ok",
  "service": "tutorsetu-api"
}
```

This endpoint verifies that the Django API is running. It intentionally does not
authenticate users or expose database details.

## Authentication

- `POST /api/auth/register/` creates a student, parent, or tutor account and
  sends an email-verification message.
- `POST /api/auth/token/` returns short-lived access and refresh JWTs.
- `POST /api/auth/token/refresh/` rotates refresh tokens.
- `POST /api/auth/logout/` blacklists the supplied refresh token.
- `GET /api/auth/me/` returns the authenticated user's safe account fields.
- `POST /api/auth/password-reset/request/` sends reset instructions with a
  generic response for both known and unknown emails.
- `POST /api/auth/password-reset/confirm/` accepts a UID, token, and validated
  replacement password.
- `POST /api/auth/verify-email/` verifies a time-limited email token.
- `POST /api/auth/verify-email/resend/` safely resends verification instructions.

Passwords and password hashes are never returned by these endpoints.
