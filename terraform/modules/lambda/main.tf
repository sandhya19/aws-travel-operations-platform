resource "aws_lambda_function" "this" {
  function_name    = var.function_name
  role             = var.role_arn
  handler          = var.handler
  runtime          = var.runtime
  filename         = var.package_file
  source_code_hash = coalesce(var.source_code_hash, filebase64sha256(var.package_file))
  timeout          = var.timeout
  memory_size      = var.memory_size
  environment { variables = var.environment_variables }
  tags = var.tags
  tracing_config { mode = "Active" }
  logging_config {
    log_format = "JSON"
    log_group  = var.log_group_name
  }
}
