# CockroachDB persistence

The API uses SQLAlchemy with the PostgreSQL-compatible `psycopg` driver. The engine
uses bounded pooling and pre-ping; each API operation receives a repository backed by
a transactional session. Failed operations roll back before the connection returns to
the pool.

Alembic revision `0001` creates travel-request metadata, indexes requester/status, and
adds a `VECTOR(1536)` column reserved for a future retrieval milestone. No AI data is
created or consumed. Run `alembic upgrade head` with `DATABASE_URL` configured.
