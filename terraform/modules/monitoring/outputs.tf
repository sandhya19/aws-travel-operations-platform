output "log_group_arn" { value = aws_cloudwatch_log_group.this.arn }
output "log_group_name" { value = aws_cloudwatch_log_group.this.name }
output "security_dashboard_name" { value = aws_cloudwatch_dashboard.security.dashboard_name }
