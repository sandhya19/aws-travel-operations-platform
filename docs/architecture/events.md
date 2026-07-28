# Travel lifecycle events

EventBridge events use source `travel.operations` and detail types:

- `TravelRequestCreated`
- `TravelValidated`
- `TravelCompleted`

Each event detail includes `request_id`, `correlation_id`, `occurred_at`, and `schema_version`.
Step Functions owns retries; failed workflow messages are retained in the SQS DLQ.
