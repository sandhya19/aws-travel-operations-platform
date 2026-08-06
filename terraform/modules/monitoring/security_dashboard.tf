resource "aws_cloudwatch_dashboard" "security" {
  # CloudWatch log groups conventionally contain slashes; dashboard names cannot.
  dashboard_name = "${replace(trim(var.name, "/"), "/", "-")}-security"
  dashboard_body = jsonencode({ widgets = [{ type = "metric", properties = { title = "Security signals", region = var.region, view = "timeSeries", metrics = [["AWS/Lambda", "Errors"], ["AWS/ApiGateway", "4XXError"], ["AWS/ApiGateway", "5XXError"]] } }] })
}
