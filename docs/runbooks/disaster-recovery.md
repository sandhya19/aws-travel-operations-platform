# CockroachDB disaster-recovery drill

This runbook proves recovery of the durable travel-case record: requests, sessions, memory
events, and tool provenance. It applies to the development CockroachDB cluster only. Do not run a
restore into the active database or use production credentials in a development drill.

## Objective and targets

- **RPO:** 60 minutes maximum between the selected backup/recovery point and drill start.
- **RTO:** 120 minutes maximum from drill start to successful verification.
- **Success:** restore to an isolated database, validate row counts for the durable tables, run a
  read-only request/memory lookup, and record the evidence JSON.

## Procedure

1. In CockroachDB Cloud, confirm the cluster's scheduled-backup/PITR status and select a recovery
   point no older than 60 minutes. Record its timestamp; do not put connection strings in evidence.
2. Create an isolated restore target according to the CockroachDB Cloud backup/restore controls
   available for the cluster tier. Never overwrite the active dev database.
3. Restore the selected recovery point, then connect to both the source snapshot reference and
   restore target with least-privilege, read-only credentials.
4. Record the counts of `travel_requests`, `agent_sessions`, `agent_memory_events`, and
   `tool_executions` in both locations. They must match for this point-in-time drill.
5. Choose a non-sensitive test request ID created for the drill and verify that its ordered memory
   history is readable in the restored target. Do not copy PII into tickets or source control.
6. Fill `docs/evidence/dr-drill.template.json` outside source control as
   `dr-drill-YYYY-MM-DD.json`, then validate it with `scripts/validate_dr_evidence.py`.
7. Delete the isolated restore target only after the evidence has been accepted, following the
   CockroachDB Cloud retention policy.

## Verification query

Run this query separately against the source point and the restore target, substituting no user
data into shell history:

```sql
SELECT 'travel_requests' AS table_name, count(*) FROM travel_requests
UNION ALL SELECT 'agent_sessions', count(*) FROM agent_sessions
UNION ALL SELECT 'agent_memory_events', count(*) FROM agent_memory_events
UNION ALL SELECT 'tool_executions', count(*) FROM tool_executions;
```

## Evidence rules

The evidence validator rejects a failed result, timestamps that exceed the RPO/RTO targets, and
mismatched durable-table counts. It is validation of an already performed restore, not a substitute
for CockroachDB Cloud backup configuration or a restore operation.
