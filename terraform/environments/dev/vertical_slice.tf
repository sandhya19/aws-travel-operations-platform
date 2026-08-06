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

module "api_role" {
  source              = "../../modules/iam"
  name                = "${local.name}-api"
  trusted_services    = ["lambda.amazonaws.com"]
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  inline_policies = {
    events   = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["events:PutEvents"], Resource = "arn:aws:events:${var.aws_region}:*:event-bus/${local.name}-travel" }] })
    database = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["secretsmanager:GetSecretValue"], Resource = [module.database_secret.secret_arn, module.cockroach_root_cert.secret_arn] }] })
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
    database = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["secretsmanager:GetSecretValue"], Resource = [module.database_secret.secret_arn, module.cockroach_root_cert.secret_arn] }] })
    decrypt  = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["kms:Decrypt"], Resource = module.database_key.key_arn }] })
  }
  tags = local.tags
}

module "eventbridge_role" {
  source           = "../../modules/iam"
  name             = "${local.name}-eventbridge"
  trusted_services = ["events.amazonaws.com"]
  inline_policies = {
    invoke_targets = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["lambda:InvokeFunction"], Resource = [module.workflow_starter_lambda.function_arn, module.outbox_dispatcher_lambda.function_arn] }] })
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
    EVENT_BUS_NAME                 = "${local.name}-travel"
    DATABASE_URL_SECRET_ARN        = module.database_secret.secret_arn
    COCKROACH_ROOT_CERT_SECRET_ARN = module.cockroach_root_cert.secret_arn
    JWT_SECRET                     = var.jwt_secret
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
  }
  tags = local.tags
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

resource "aws_cloudwatch_event_rule" "outbox_dispatcher" {
  name                = "${local.name}-outbox-dispatch"
  schedule_expression = "rate(1 minute)"
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
        Next       = "Complete"
        Catch      = [{ ErrorEquals = ["States.ALL"], ResultPath = "$.error", Next = "WorkflowFailed" }]
      }
      Complete = {
        Type       = "Task"
        Resource   = module.workflow_lambda.function_arn
        Parameters = { action = "COMPLETE", "request_id.$" = "$.detail.request_id" }
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
