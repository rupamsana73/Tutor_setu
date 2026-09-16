# TutorSetu Phase 1 Database

Phase 1 configures PostgreSQL as the only application database. No marketplace
models are created yet; this keeps the foundation small while the domain model is
defined in a later phase.

Required environment variables:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

Never place production credentials in source control or `.env.example`.
