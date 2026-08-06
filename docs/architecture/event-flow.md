# Implemented event flow

The intended lifecycle is:

1. The API persists metadata and emits `TravelRequestCreated` to the custom EventBridge bus.
2. EventBridge starts the Standard Step Functions state machine, with three delivery retries
   and an SQS dead-letter queue.
3. The workflow Lambda validates the event then records the callback task token in
   CockroachDB's `approval_tasks` table.
4. An authenticated caller posts an approval decision; the API resolves the Step Functions
   callback. The callback output is stored at `$.approval`, preserving the original event
   detail; the workflow then marks that request `COMPLETED`.

This vertical slice intentionally stops at human approval. Policy, visa, risk, insurance,
recommendation, and AI event contracts remain outside IMP-003.

## Workflow

The deployed IMP-003 workflow is defined in `terraform/environments/dev/vertical_slice.tf`:
validation, callback-based human approval, then completion. Validation retries up to three
times; human approval is the only transition that authorizes completion.
