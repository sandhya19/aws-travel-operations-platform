resource "aws_sfn_state_machine" "this" {
  name       = var.name
  role_arn   = var.role_arn
  definition = var.definition
  type       = var.type

  logging_configuration {
    include_execution_data = true
    level                  = var.log_level
    log_destination        = "${var.log_group_arn}:*"
  }
  tracing_configuration { enabled = true }
  tags = var.tags
}
