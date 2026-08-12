module "workflow_logs" {
  source = "../../modules/monitoring"
  name   = "/aws/vendedlogs/states/${local.name}-travel-workflow"
  tags   = local.tags
}

module "workflow_dlq" {
  source = "../../modules/sqs"
  name   = "${local.name}-travel-events"
  tags   = local.tags
}

module "database_key" {
  source      = "../../modules/kms"
  alias       = "${local.name}-database"
  description = "Encrypts ${local.name} CockroachDB credentials"
  tags        = local.tags
}

module "database_secret" {
  source                  = "../../modules/secrets_manager"
  name                    = "${local.name}/database-url"
  description             = "CockroachDB connection URL for ${local.name}"
  kms_key_arn             = module.database_key.key_arn
  secret_string           = var.database_url
  recovery_window_in_days = 7
  tags                    = local.tags
}

module "cockroach_root_cert" {
  source                  = "../../modules/secrets_manager"
  name                    = "${local.name}/cockroach-root-cert"
  description             = "CockroachDB TLS root certificate for ${local.name}"
  kms_key_arn             = module.database_key.key_arn
  secret_string           = var.cockroach_root_cert_pem
  recovery_window_in_days = 7
  tags                    = local.tags
}

module "jwt_secret" {
  source                  = "../../modules/secrets_manager"
  name                    = "${local.name}/jwt-secret"
  description             = "JWT signing secret for ${local.name}"
  kms_key_arn             = module.database_key.key_arn
  secret_string           = var.jwt_secret
  recovery_window_in_days = 7
  tags                    = local.tags
}

module "knowledge_bucket" {
  source      = "../../modules/s3"
  name        = var.knowledge_bucket_name
  kms_key_arn = module.database_key.key_arn
  tags        = local.tags
}

module "rag_guardrail" {
  source                  = "../../modules/bedrock"
  name                    = "${local.name}-rag-safety"
  description             = "Baseline safety messaging for future grounded-answer model invocation"
  blocked_input_messaging = "The request could not be processed safely."
  blocked_outputs_messaging = (
    "The response could not be produced safely from approved travel policy evidence."
  )
  tags = local.tags
}

module "api_role" {
  source              = "../../modules/iam"
  name                = "${local.name}-api"
  trusted_services    = ["lambda.amazonaws.com"]
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policies = {
    events   = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["events:PutEvents"], Resource = "arn:aws:events:${var.aws_region}:*:event-bus/${local.name}-travel" }] })
    database = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["secretsmanager:GetSecretValue"], Resource = [module.database_secret.secret_arn, module.cockroach_root_cert.secret_arn, module.jwt_secret.secret_arn] }] })
    decrypt  = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["kms:Decrypt"], Resource = module.database_key.key_arn }] })
    workflow = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["states:SendTaskSuccess"], Resource = "*" }] })
  }
  tags = local.tags
}

module "workflow_role" {
  source           = "../../modules/iam"
  name             = "${local.name}-workflow"
  trusted_services = ["states.amazonaws.com"]
  inline_policies = {
    invoke  = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["lambda:InvokeFunction"], Resource = module.workflow_lambda.function_arn }] })
    logging = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["logs:CreateLogDelivery", "logs:GetLogDelivery", "logs:UpdateLogDelivery", "logs:DeleteLogDelivery", "logs:ListLogDeliveries", "logs:PutResourcePolicy", "logs:DescribeResourcePolicies", "logs:DescribeLogGroups"], Resource = "*" }] })
  }
  tags = local.tags
}

module "workflow_lambda_role" {
  source              = "../../modules/iam"
  name                = "${local.name}-workflow-lambda"
  trusted_services    = ["lambda.amazonaws.com"]
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policies = {
    database = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["secretsmanager:GetSecretValue"], Resource = [module.database_secret.secret_arn, module.cockroach_root_cert.secret_arn] }] })
    decrypt  = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["kms:Decrypt"], Resource = module.database_key.key_arn }] })
  }
  tags = local.tags
}

module "workflow_starter_role" {
  source              = "../../modules/iam"
  name                = "${local.name}-workflow-starter"
  trusted_services    = ["lambda.amazonaws.com"]
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policies = {
    start_workflow = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["states:StartExecution"], Resource = module.travel_workflow.state_machine_arn }] })
  }
  tags = local.tags
}

module "outbox_dispatcher_role" {
  source              = "../../modules/iam"
  name                = "${local.name}-outbox-dispatcher"
  trusted_services    = ["lambda.amazonaws.com"]
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policies = {
    events   = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["events:PutEvents"], Resource = module.events.event_bus_arn }] })
    dlq      = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["sqs:SendMessage"], Resource = module.workflow_dlq.dlq_arn }] })
    database = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["secretsmanager:GetSecretValue"], Resource = [module.database_secret.secret_arn, module.cockroach_root_cert.secret_arn] }] })
    decrypt  = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["kms:Decrypt"], Resource = module.database_key.key_arn }] })
  }
  tags = local.tags
}

module "memory_lifecycle_role" {
  source              = "../../modules/iam"
  name                = "${local.name}-memory-lifecycle"
  trusted_services    = ["lambda.amazonaws.com"]
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policies = {
    database = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["secretsmanager:GetSecretValue"], Resource = [module.database_secret.secret_arn, module.cockroach_root_cert.secret_arn] }] })
    decrypt  = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["kms:Decrypt"], Resource = module.database_key.key_arn }] })
  }
  tags = local.tags
}

module "document_ingestion_role" {
  source              = "../../modules/iam"
  name                = "${local.name}-document-ingestion"
  trusted_services    = ["lambda.amazonaws.com"]
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policies = {
    read_documents  = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["s3:GetObject", "s3:GetObjectVersion"], Resource = "${module.knowledge_bucket.bucket_arn}/*" }] })
    embed_documents = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["bedrock:InvokeModel"], Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v2:0" }] })
    database        = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["secretsmanager:GetSecretValue"], Resource = [module.database_secret.secret_arn, module.cockroach_root_cert.secret_arn] }] })
    decrypt         = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["kms:Decrypt"], Resource = module.database_key.key_arn }] })
  }
  tags = local.tags
}

module "agent_tools_role" {
  source              = "../../modules/iam"
  name                = "${local.name}-agent-tools"
  trusted_services    = ["lambda.amazonaws.com"]
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policies = {
    database = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["secretsmanager:GetSecretValue"], Resource = [module.database_secret.secret_arn, module.cockroach_root_cert.secret_arn] }] })
    decrypt  = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["kms:Decrypt"], Resource = module.database_key.key_arn }] })
  }
  tags = local.tags
}

module "agent_runtime_artifacts" {
  source      = "../../modules/s3"
  name        = "${local.name}-agent-runtime-${data.aws_caller_identity.current.account_id}"
  kms_key_arn = module.database_key.key_arn
  tags        = local.tags
}

module "agentcore_runtime_role" {
  source           = "../../modules/iam"
  name             = "${local.name}-agentcore-runtime"
  trusted_services = ["bedrock-agentcore.amazonaws.com"]
  inline_policies = {
    invoke_tool  = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["lambda:InvokeFunction"], Resource = module.agent_tools_lambda.function_arn }] })
    read_package = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["s3:GetObject", "s3:GetObjectVersion"], Resource = "${module.agent_runtime_artifacts.bucket_arn}/*" }] })
    decrypt      = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["kms:Decrypt"], Resource = module.database_key.key_arn }] })
  }
  tags = local.tags
}

module "eventbridge_role" {
  source           = "../../modules/iam"
  name             = "${local.name}-eventbridge"
  trusted_services = ["events.amazonaws.com"]
  inline_policies = {
    invoke_targets = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["lambda:InvokeFunction"], Resource = [module.workflow_starter_lambda.function_arn, module.outbox_dispatcher_lambda.function_arn, module.memory_lifecycle_lambda.function_arn] }] })
  }
  tags = local.tags
}

module "api_lambda" {
  source         = "../../modules/lambda"
  function_name  = "${local.name}-api"
  description    = "Travel request API"
  role_arn       = module.api_role.role_arn
  handler        = "travel_operations.api.main.handler"
  package_file   = var.api_package_file
  log_group_name = "/aws/lambda/${local.name}-api"
  environment_variables = {
    ENVIRONMENT                        = var.environment
    EVENT_BUS_NAME                     = "${local.name}-travel"
    DATABASE_URL_SECRET_ARN            = module.database_secret.secret_arn
    COCKROACH_ROOT_CERT_SECRET_ARN     = module.cockroach_root_cert.secret_arn
    JWT_SECRET_SECRET_ARN              = module.jwt_secret.secret_arn
    SIMULATE_APPROVAL_CALLBACK_FAILURE = tostring(var.simulate_approval_callback_failure)
    MEMORY_RETENTION_DAYS              = tostring(var.memory_retention_days)
  }
  tags = local.tags
}

module "workflow_lambda" {
  source         = "../../modules/lambda"
  function_name  = "${local.name}-workflow"
  description    = "Travel approval workflow handlers"
  role_arn       = module.workflow_lambda_role.role_arn
  handler        = "travel_operations.workflow_handlers.handler"
  package_file   = var.api_package_file
  log_group_name = "/aws/lambda/${local.name}-workflow"
  environment_variables = {
    DATABASE_URL_SECRET_ARN        = module.database_secret.secret_arn
    COCKROACH_ROOT_CERT_SECRET_ARN = module.cockroach_root_cert.secret_arn
  }
  tags = local.tags
}

module "workflow_starter_lambda" {
  source         = "../../modules/lambda"
  function_name  = "${local.name}-workflow-starter"
  description    = "Idempotently starts travel workflows"
  role_arn       = module.workflow_starter_role.role_arn
  handler        = "travel_operations.workflow_starter.handler"
  package_file   = var.api_package_file
  log_group_name = "/aws/lambda/${local.name}-workflow-starter"
  environment_variables = {
    WORKFLOW_STATE_MACHINE_ARN = module.travel_workflow.state_machine_arn
  }
  tags = local.tags
}

module "outbox_dispatcher_lambda" {
  source         = "../../modules/lambda"
  function_name  = "${local.name}-outbox-dispatcher"
  description    = "Retries unpublished travel workflow events"
  role_arn       = module.outbox_dispatcher_role.role_arn
  handler        = "travel_operations.outbox_dispatcher.handler"
  package_file   = var.api_package_file
  log_group_name = "/aws/lambda/${local.name}-outbox-dispatcher"
  environment_variables = {
    DATABASE_URL_SECRET_ARN        = module.database_secret.secret_arn
    COCKROACH_ROOT_CERT_SECRET_ARN = module.cockroach_root_cert.secret_arn
    EVENT_BUS_NAME                 = module.events.event_bus_name
    OUTBOX_DLQ_URL                 = module.workflow_dlq.dlq_url
    OUTBOX_MAX_ATTEMPTS            = "3"
  }
  tags = local.tags
}

module "memory_lifecycle_lambda" {
  source         = "../../modules/lambda"
  function_name  = "${local.name}-memory-lifecycle"
  description    = "Expires terminal travel-case memory sessions"
  role_arn       = module.memory_lifecycle_role.role_arn
  handler        = "travel_operations.memory_lifecycle.handler"
  package_file   = var.api_package_file
  log_group_name = "/aws/lambda/${local.name}-memory-lifecycle"
  environment_variables = {
    DATABASE_URL_SECRET_ARN        = module.database_secret.secret_arn
    COCKROACH_ROOT_CERT_SECRET_ARN = module.cockroach_root_cert.secret_arn
  }
  tags = local.tags
}

module "document_ingestion_lambda" {
  source         = "../../modules/lambda"
  function_name  = "${local.name}-document-ingestion"
  description    = "Validates and versions tenant knowledge PDFs"
  role_arn       = module.document_ingestion_role.role_arn
  handler        = "travel_operations.document_ingestion.handler"
  package_file   = var.api_package_file
  log_group_name = "/aws/lambda/${local.name}-document-ingestion"
  timeout        = 60
  environment_variables = {
    KNOWLEDGE_BUCKET               = module.knowledge_bucket.bucket_id
    DATABASE_URL_SECRET_ARN        = module.database_secret.secret_arn
    COCKROACH_ROOT_CERT_SECRET_ARN = module.cockroach_root_cert.secret_arn
  }
  tags = local.tags
}

module "agent_tools_lambda" {
  source         = "../../modules/lambda"
  function_name  = "${local.name}-agent-tools"
  description    = "Records typed AgentCore tool invocations"
  role_arn       = module.agent_tools_role.role_arn
  handler        = "travel_operations.agent_tools.handler"
  package_file   = var.api_package_file
  log_group_name = "/aws/lambda/${local.name}-agent-tools"
  environment_variables = {
    DATABASE_URL_SECRET_ARN        = module.database_secret.secret_arn
    COCKROACH_ROOT_CERT_SECRET_ARN = module.cockroach_root_cert.secret_arn
  }
  tags = local.tags
}

resource "aws_s3_object" "agent_runtime_package" {
  bucket                 = module.agent_runtime_artifacts.bucket_id
  key                    = "releases/${filemd5(var.agent_runtime_package_file)}.zip"
  source                 = var.agent_runtime_package_file
  source_hash            = filebase64sha256(var.agent_runtime_package_file)
  server_side_encryption = "aws:kms"
  kms_key_id             = module.database_key.key_arn
}

resource "aws_bedrockagentcore_agent_runtime" "travel_operations" {
  agent_runtime_name = "${replace(var.project_name, "-", "_")}_${var.environment}"
  description        = "Tenant-scoped travel-policy tool coordinator with durable provenance"
  role_arn           = module.agentcore_runtime_role.role_arn

  agent_runtime_artifact {
    code_configuration {
      code {
        s3 {
          bucket = module.agent_runtime_artifacts.bucket_id
          prefix = aws_s3_object.agent_runtime_package.key
        }
      }
      entry_point = ["agent.py"]
      runtime     = "PYTHON_3_12"
    }
  }

  environment_variables = {
    AGENT_TOOLS_FUNCTION_NAME = module.agent_tools_lambda.function_name
  }

  network_configuration { network_mode = "PUBLIC" }
  protocol_configuration { server_protocol = "HTTP" }
  tags = local.tags
}

resource "aws_lambda_permission" "agentcore_runtime_tools" {
  statement_id  = "AgentCoreRuntimeToolInvocation"
  action        = "lambda:InvokeFunction"
  function_name = module.agent_tools_lambda.function_name
  principal     = "bedrock-agentcore.amazonaws.com"
  source_arn    = aws_bedrockagentcore_agent_runtime.travel_operations.agent_runtime_arn
}

resource "aws_lambda_permission" "knowledge_bucket_document_ingestion" {
  statement_id  = "KnowledgeBucketDocumentIngestion"
  action        = "lambda:InvokeFunction"
  function_name = module.document_ingestion_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = module.knowledge_bucket.bucket_arn
}

resource "aws_s3_bucket_notification" "knowledge_document_ingestion" {
  bucket = module.knowledge_bucket.bucket_id
  lambda_function {
    lambda_function_arn = module.document_ingestion_lambda.function_arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".pdf"
  }
  depends_on = [aws_lambda_permission.knowledge_bucket_document_ingestion]
}

module "events" {
  source = "../../modules/eventbridge"
  name   = "${local.name}-travel"
  rules = {
    created = {
      event_pattern                = jsonencode({ source = ["travel.operations"], "detail-type" = ["TravelRequestCreated"] })
      target_arn                   = module.workflow_starter_lambda.function_arn
      dlq_arn                      = module.workflow_dlq.queue_arn
      maximum_event_age_in_seconds = 3600
      maximum_retry_attempts       = 3
      role_arn                     = module.eventbridge_role.role_arn
    }
  }
  tags = local.tags
}

resource "aws_lambda_permission" "eventbridge_workflow_starter" {
  statement_id  = "EventBridgeWorkflowStarter"
  action        = "lambda:InvokeFunction"
  function_name = module.workflow_starter_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = module.events.rule_arns["created"]
}

resource "aws_lambda_permission" "eventbridge_outbox_dispatcher" {
  statement_id  = "EventBridgeOutboxDispatcher"
  action        = "lambda:InvokeFunction"
  function_name = module.outbox_dispatcher_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.outbox_dispatcher.arn
}

resource "aws_lambda_permission" "eventbridge_memory_lifecycle" {
  statement_id  = "EventBridgeMemoryLifecycle"
  action        = "lambda:InvokeFunction"
  function_name = module.memory_lifecycle_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.memory_lifecycle.arn
}

resource "aws_cloudwatch_event_rule" "outbox_dispatcher" {
  name                = "${local.name}-outbox-dispatch"
  schedule_expression = "rate(1 minute)"
  tags                = local.tags
}

resource "aws_cloudwatch_event_rule" "memory_lifecycle" {
  name                = "${local.name}-memory-lifecycle"
  schedule_expression = "rate(1 day)"
  tags                = local.tags
}

resource "aws_cloudwatch_event_target" "outbox_dispatcher" {
  rule      = aws_cloudwatch_event_rule.outbox_dispatcher.name
  target_id = "outbox-dispatcher"
  arn       = module.outbox_dispatcher_lambda.function_arn

  dead_letter_config { arn = module.workflow_dlq.queue_arn }
  retry_policy {
    maximum_event_age_in_seconds = 3600
    maximum_retry_attempts       = 3
  }
}

resource "aws_cloudwatch_event_target" "memory_lifecycle" {
  rule      = aws_cloudwatch_event_rule.memory_lifecycle.name
  target_id = "memory-lifecycle"
  arn       = module.memory_lifecycle_lambda.function_arn
}

module "travel_workflow" {
  source        = "../../modules/step_functions"
  name          = "${local.name}-travel-request"
  role_arn      = module.workflow_role.role_arn
  log_group_arn = module.workflow_logs.log_group_arn
  definition = jsonencode({
    StartAt = "Validate"
    States = {
      Validate = {
        Type     = "Task"
        Resource = module.workflow_lambda.function_arn
        Next     = "AwaitApproval"
        Retry    = [{ ErrorEquals = ["States.ALL"], MaxAttempts = 3 }]
        Catch    = [{ ErrorEquals = ["States.ALL"], ResultPath = "$.error", Next = "WorkflowFailed" }]
      }
      AwaitApproval = {
        Type       = "Task"
        Resource   = "arn:aws:states:::lambda:invoke.waitForTaskToken"
        Parameters = { FunctionName = module.workflow_lambda.function_arn, Payload = { "TaskToken.$" = "$$.Task.Token", "detail.$" = "$.detail" } }
        ResultPath = "$.approval"
        Next       = "ApprovalDecision"
        Catch      = [{ ErrorEquals = ["States.ALL"], ResultPath = "$.error", Next = "WorkflowFailed" }]
      }
      ApprovalDecision = {
        Type    = "Choice"
        Choices = [{ Variable = "$.approval.approved", BooleanEquals = true, Next = "Complete" }]
        Default = "Reject"
      }
      Complete = {
        Type       = "Task"
        Resource   = module.workflow_lambda.function_arn
        Parameters = { action = "COMPLETE", "request_id.$" = "$.detail.request_id" }
        End        = true
        Catch      = [{ ErrorEquals = ["States.ALL"], ResultPath = "$.error", Next = "WorkflowFailed" }]
      }
      Reject = {
        Type       = "Task"
        Resource   = module.workflow_lambda.function_arn
        Parameters = { action = "REJECT", "request_id.$" = "$.detail.request_id" }
        End        = true
        Catch      = [{ ErrorEquals = ["States.ALL"], ResultPath = "$.error", Next = "WorkflowFailed" }]
      }
      WorkflowFailed = { Type = "Fail", Error = "TravelWorkflowFailed", Cause = "See execution error details" }
    }
  })
  tags = local.tags
}

module "api" {
  source               = "../../modules/api_gateway"
  name                 = "${local.name}-api"
  description          = "Travel request API"
  access_log_group_arn = module.workflow_logs.log_group_arn
  routes = {
    api = { route_key = "ANY /{proxy+}", invoke_arn = module.api_lambda.invoke_arn, function_name = module.api_lambda.function_name }
  }
  tags = local.tags
}
