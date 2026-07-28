# Planned event flow

The intended lifecycle is:

1. `TravelRequestSubmitted`
2. `TravelRequestValidated`
3. `PolicyRetrieved`
4. `VisaChecked`
5. `RiskAssessed`
6. `InsuranceCalculated`
7. `RecommendationGenerated`
8. `ApprovalRequested`
9. `ApprovalCompleted`
10. `TravelRequestCompleted`

Event contracts, ownership, ordering, retry policy, schema evolution, and idempotency
requirements are deferred to Milestone 3.
