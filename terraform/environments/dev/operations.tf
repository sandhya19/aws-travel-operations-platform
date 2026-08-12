module "operations_alerts" {
  source      = "../../modules/sns"
  name        = "${local.name}-operations-alerts"
  kms_key_arn = module.database_key.key_arn
  subscriptions = var.operations_alert_email == null ? {} : {
    email = {
      protocol = "email"
      endpoint = var.operations_alert_email
    }
  }
  tags = local.tags
}

locals {
  monitored_lambda_functions = {
    api               = module.api_lambda.function_name
    workflow          = module.workflow_lambda.function_name
    workflow_starter  = module.workflow_starter_lambda.function_name
    outbox_dispatcher = module.outbox_dispatcher_lambda.function_name
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  for_each            = local.monitored_lambda_functions
  alarm_name          = "${local.name}-${each.key}-errors"
  alarm_description   = "Investigate ${each.key} Lambda errors using the operations runbook."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"
  alarm_actions       = [module.operations_alerts.topic_arn]
  ok_actions          = [module.operations_alerts.topic_arn]

  dimensions = { FunctionName = each.value }
}

resource "aws_cloudwatch_metric_alarm" "workflow_failures" {
  alarm_name          = "${local.name}-workflow-failures"
  alarm_description   = "A travel Step Functions execution failed. Preserve evidence before retrying."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ExecutionsFailed"
  namespace           = "AWS/States"
  period              = 300
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"
  alarm_actions       = [module.operations_alerts.topic_arn]
  ok_actions          = [module.operations_alerts.topic_arn]

  dimensions = { StateMachineArn = module.travel_workflow.state_machine_arn }
}

resource "aws_cloudwatch_metric_alarm" "dlq_depth" {
  alarm_name          = "${local.name}-workflow-dlq-visible-messages"
  alarm_description   = "A workflow recovery message is waiting in the DLQ. Follow the recovery runbook."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Maximum"
  threshold           = 1
  treat_missing_data  = "notBreaching"
  alarm_actions       = [module.operations_alerts.topic_arn]
  ok_actions          = [module.operations_alerts.topic_arn]

  dimensions = { QueueName = "${local.name}-travel-events-dlq" }
}

resource "aws_cloudwatch_metric_alarm" "api_client_errors" {
  alarm_name          = "${local.name}-api-authentication-and-client-errors"
  alarm_description   = "API 4XX errors include rejected authentication and authorization requests; inspect access logs."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "4xx"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  treat_missing_data  = "notBreaching"
  alarm_actions       = [module.operations_alerts.topic_arn]
  ok_actions          = [module.operations_alerts.topic_arn]

  dimensions = { ApiId = module.api.api_id }
}

resource "aws_cloudwatch_metric_alarm" "api_latency" {
  alarm_name          = "${local.name}-api-latency"
  alarm_description   = "The API p99 latency exceeded the dev SLO. Inspect X-Ray and Lambda metrics."
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Latency"
  namespace           = "AWS/ApiGateway"
  period              = 300
  extended_statistic  = "p99"
  threshold           = 3000
  treat_missing_data  = "notBreaching"
  alarm_actions       = [module.operations_alerts.topic_arn]
  ok_actions          = [module.operations_alerts.topic_arn]

  dimensions = { ApiId = module.api.api_id }
}

resource "aws_cloudwatch_metric_alarm" "kms_key_errors" {
  alarm_name          = "${local.name}-kms-key-errors"
  alarm_description   = "KMS key errors may block secret, queue, topic, or object access. Investigate immediately."
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "KMSKeyError"
  namespace           = "AWS/KMS"
  period              = 300
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"
  alarm_actions       = [module.operations_alerts.topic_arn]
  ok_actions          = [module.operations_alerts.topic_arn]

  dimensions = { KeyId = module.database_key.key_arn }
}

resource "aws_cloudwatch_dashboard" "operations" {
  dashboard_name = "${local.name}-operations"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          title  = "Workflow health"
          region = var.aws_region
          view   = "timeSeries"
          metrics = [
            ["AWS/States", "ExecutionsSucceeded", "StateMachineArn", module.travel_workflow.state_machine_arn],
            ["AWS/States", "ExecutionsFailed", "StateMachineArn", module.travel_workflow.state_machine_arn],
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", "${local.name}-travel-events-dlq"]
          ]
        }
      },
      {
        type = "metric"
        properties = {
          title  = "API security and latency"
          region = var.aws_region
          view   = "timeSeries"
          metrics = [
            ["AWS/ApiGateway", "4xx", "ApiId", module.api.api_id],
            ["AWS/ApiGateway", "5xx", "ApiId", module.api.api_id],
            ["AWS/ApiGateway", "Latency", "ApiId", module.api.api_id, { stat = "p99" }]
          ]
        }
      },
      {
        type = "metric"
        properties = {
          title  = "Lambda and KMS failures"
          region = var.aws_region
          view   = "timeSeries"
          metrics = concat(
            [for function_name in values(local.monitored_lambda_functions) : ["AWS/Lambda", "Errors", "FunctionName", function_name]],
            [["AWS/KMS", "KMSKeyError", "KeyId", module.database_key.key_arn]]
          )
        }
      }
    ]
  })
}
