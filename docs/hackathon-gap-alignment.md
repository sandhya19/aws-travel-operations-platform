# Hackathon gap alignment

The current review gaps map to the existing implementation roadmap; they do not require a system
redesign.

| Review gap | Roadmap item | Intended evidence |
| --- | --- | --- |
| Evaluation benchmark and promotion gates | IMP-018 | Reproducible golden results and a failed-release gate |
| Cloud E2E, integration, and CI enforcement | IMP-019 | Automated authenticated AWS and CockroachDB runs |
| Fault/load testing | IMP-020 | Documented recovery and throughput limits |
| Alarms and operational dashboards | IMP-021 | Alarm tests and response runbooks |
| Backup/restore proof | IMP-022 | Recorded RPO/RTO restore drill |
| Cost/latency business evidence | IMP-023 | Measured baseline and assisted comparison |
| Reviewer reset and scripted walkthrough | IMP-024 | One-command sandbox reset |
| Submission demo and evidence pack | IMP-025 | Recorded demo and truthful proof index |

Two gaps are deliberate current-scope limits: AgentCore presently demonstrates durable, scoped tool
provenance for `lookup_policy`, and the grounded-answer service has no model-backed public API.
Future work must connect retrieval, a guarded model invocation, citations, and safety-decision
provenance rather than represent the current placeholder tool response as a recommendation.
