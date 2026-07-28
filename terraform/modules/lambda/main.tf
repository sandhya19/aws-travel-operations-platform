resource "aws_lambda_function" "this" {
  function_name = var.function_name
  role          = var.role_arn
  handler       = var.handler
  runtime       = var.runtime
  filename      = var.package_file
  timeout       = var.timeout
  memory_size   = var.memory_size
  tracing_config { mode = "Active" }
  logging_config {
    log_format = "JSON"
    log_group  = var.log_group_name
  }
}
