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
