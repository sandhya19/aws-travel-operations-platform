"""Contract checks for the deployable IMP-003 workflow definition."""

import re
from pathlib import Path


def test_approval_callback_preserves_request_detail() -> None:
    """Completion must retain the EventBridge request identifier after approval."""
    definition = (
        Path(__file__).parents[2] / "terraform" / "environments" / "dev" / "vertical_slice.tf"
    ).read_text(encoding="utf-8")

    assert 'ResultPath = "$.approval"' in definition
    assert '"request_id.$" = "$.detail.request_id"' in definition
    assert 'Next = "WorkflowFailed"' in definition
    assert 'WorkflowFailed = { Type = "Fail"' in definition


def test_lambdas_read_database_url_from_the_kms_encrypted_secret() -> None:
    """Both Lambda roles must be able to read and decrypt the database secret."""
    definition = (
        Path(__file__).parents[2] / "terraform" / "environments" / "dev" / "vertical_slice.tf"
    ).read_text(encoding="utf-8")

    assert re.search(r"DATABASE_URL_SECRET_ARN\s+= module\.database_secret\.secret_arn", definition)
    assert definition.count('Action = ["secretsmanager:GetSecretValue"]') >= 2
    assert definition.count('Action = ["kms:Decrypt"]') >= 2


def test_api_reads_jwt_from_a_dedicated_runtime_secret() -> None:
    definition = (
        Path(__file__).parents[2] / "terraform" / "environments" / "dev" / "vertical_slice.tf"
    ).read_text(encoding="utf-8")

    assert 'name                    = "${local.name}/jwt-secret"' in definition
    assert re.search(r"JWT_SECRET_SECRET_ARN\s+= module\.jwt_secret\.secret_arn", definition)
    assert "JWT_SECRET                     = var.jwt_secret" not in definition
    assert "module.jwt_secret.secret_arn" in definition


def test_outbox_dispatcher_can_route_exhausted_events_to_the_dlq() -> None:
    """The dispatcher needs an explicit DLQ URL and narrowly scoped send permission."""
    definition = (
        Path(__file__).parents[2] / "terraform" / "environments" / "dev" / "vertical_slice.tf"
    ).read_text(encoding="utf-8")

    assert 'Action = ["sqs:SendMessage"]' in definition
    assert "Resource = module.workflow_dlq.dlq_arn" in definition
    assert "OUTBOX_DLQ_URL                 = module.workflow_dlq.dlq_url" in definition
    assert 'OUTBOX_MAX_ATTEMPTS            = "3"' in definition


def test_document_ingestion_has_scoped_s3_and_titan_permissions() -> None:
    definition = (
        Path(__file__).parents[2] / "terraform" / "environments" / "dev" / "vertical_slice.tf"
    ).read_text(encoding="utf-8")

    assert 'Action = ["s3:GetObject", "s3:GetObjectVersion"]' in definition
    assert 'Action = ["bedrock:InvokeModel"]' in definition
    assert 'handler        = "travel_operations.document_ingestion.handler"' in definition
    assert "aws_s3_bucket_notification" in definition


def test_rag_guardrail_has_safe_input_and_output_messages() -> None:
    definition = (
        Path(__file__).parents[2] / "terraform" / "environments" / "dev" / "vertical_slice.tf"
    ).read_text(encoding="utf-8")

    assert 'module "rag_guardrail"' in definition
    assert 'source                  = "../../modules/bedrock"' in definition
    assert "could not be processed safely" in definition
    assert "could not be produced safely" in definition

    module_definition = (
        Path(__file__).parents[2] / "terraform" / "modules" / "bedrock" / "main.tf"
    ).read_text(encoding="utf-8")
    assert 'type            = "PROMPT_ATTACK"' in module_definition
    assert 'input_strength  = "HIGH"' in module_definition
    assert 'output_strength = "NONE"' in module_definition


def test_agentcore_runtime_uses_a_scoped_typed_tool_lambda() -> None:
    definition = (
        Path(__file__).parents[2] / "terraform" / "environments" / "dev" / "vertical_slice.tf"
    ).read_text(encoding="utf-8")

    assert 'resource "aws_bedrockagentcore_agent_runtime" "travel_operations"' in definition
    runtime_name = (
        'agent_runtime_name = "${replace(var.project_name, "-", "_")}_'
        '${var.environment}"'
    )
    assert runtime_name in definition
    assert 'trusted_services = ["bedrock-agentcore.amazonaws.com"]' in definition
    assert 'Action = ["lambda:InvokeFunction"]' in definition
    assert "source_hash            = filebase64sha256(var.agent_runtime_package_file)" in definition
    assert "etag                   = filemd5(var.agent_runtime_package_file)" not in definition
    assert 'handler        = "travel_operations.agent_tools.handler"' in definition
    assert 'principal     = "bedrock-agentcore.amazonaws.com"' in definition


def test_operations_alarms_cover_dlq_auth_kms_errors_and_latency() -> None:
    operations = (
        Path(__file__).parents[2] / "terraform" / "environments" / "dev" / "operations.tf"
    ).read_text(encoding="utf-8")

    assert 'module "operations_alerts"' in operations
    assert 'metric_name         = "ApproximateNumberOfMessagesVisible"' in operations
    assert 'metric_name         = "4xx"' in operations
    assert 'metric_name         = "KMSKeyError"' in operations
    assert 'metric_name         = "Latency"' in operations
    assert 'resource "aws_cloudwatch_dashboard" "operations"' in operations
