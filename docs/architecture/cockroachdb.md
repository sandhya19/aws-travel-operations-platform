# CockroachDB persistence

The API uses SQLAlchemy with the PostgreSQL-compatible `psycopg` driver. The engine
uses bounded pooling and pre-ping; each API operation receives a repository backed by
a transactional session. Failed operations roll back before the connection returns to
the pool.

Alembic revision `0001` creates travel-request metadata, indexes requester/status, and
adds a `VECTOR(1536)` column reserved for a future retrieval milestone. Revision `0007` adds
`agent_sessions` and append-only `agent_memory_events`: each session is tied to one travel
request and carries tenant, user, and correlation identifiers; every event records its actor,
source, type, payload, and timestamp. Revision `0011` assigns every travel request a non-null
tenant identifier and backfills pre-existing records to `default`. The
`tenant_id, requester_id, status` index supports authorization-filtered request and memory
lookup plans. User-facing repository methods must use the tenant-scoped request/session queries;
unscoped request lookup is reserved for trusted workflow transitions.

The current foundation captures operational workflow history. It does not yet provide agent
tool/plan provenance, checkpoint/replay, physical deletion, or cross-session retrieval. Run
`alembic upgrade head` with `DATABASE_URL` configured.

Memory sessions now receive a retention expiry at creation. The scheduled lifecycle handler
marks only terminal (`COMPLETED` or `REJECTED`) sessions expired and records immutable expiry
evidence. It does not physically purge data; deletion and consolidation require a later,
explicit privacy workflow.

Revision `0012` adds `knowledge_documents` for immutable tenant-owned source versions. It also
adds `tenant_id` and `page_number` to `knowledge_chunks`, with a tenant/document/version index for
the next scoped retrieval increment. Existing chunks are backfilled to the `default` tenant.

Revision `0013` adds `knowledge_document_access`, keyed by document and role. Retrieval uses a
tenant predicate and a role existence predicate before CockroachDB vector ordering, preventing
cross-tenant and unauthorized-document context from entering a grounded answer.
