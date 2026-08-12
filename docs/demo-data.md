# Demo data

Run `poetry run python scripts/seed_data.py` after migrations. It creates one safe, fictional travel request for `demo.employee`; it contains no PII or production policy content.

## Deployed dev demonstration

With `JWT_SECRET` set from the ignored `.env`, run:

```bash
python scripts/run_dev_workflow_demo.py --api-url "$(terraform -chdir=terraform/environments/dev output -raw travel_api_endpoint)"
```

The runner creates a request, waits for the callback task, submits authorized approval, and
prints its ID only after the API reports `COMPLETED`.

The same runner is the opt-in cloud E2E test; see the developer guide for the secure command and
environment requirements.

## AgentCore itinerary orchestration

After creating a travel request, invoke the deployed AgentCore Runtime with that request ID,
tenant ID, and user ID. The centralized coordinator delegates a fixed policy/compliance review,
risk review, inventory research, itinerary-draft, and financial-triage plan. Its response is
deliberately a human-review draft: policy and risk results do not claim approval, and the itinerary
is never booked.

Inspect `tool_executions` and `agent_memory_events` for the six delegated specialist calls. This
is the demonstrable CockroachDB provenance story for the hackathon.

## Interactive customer itinerary demo

The fastest demo path is the authenticated API. Submit one requirement and receive a transparent,
non-booking draft with profile, policy/compliance, risk, inventory-research, itinerary, and
financial-triage specialist results. The same request enters the existing human approval workflow.

```bash
curl -sS -X POST "$API_URL/itineraries" \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "destination_country": "GB",
    "departure_date": "2026-11-10",
    "return_date": "2026-11-14",
    "purpose": "Customer workshop with client meetings",
    "travelers": 2,
    "budget_amount": 3000,
    "budget_currency": "GBP",
    "interests": ["food", "art"]
  }'
```

Use the returned `travel_request_id` with the memory endpoint to show the durable decision trail.
