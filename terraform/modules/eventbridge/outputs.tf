output "event_bus_arn" { value = aws_cloudwatch_event_bus.this.arn }
output "event_bus_name" { value = aws_cloudwatch_event_bus.this.name }
output "rule_arns" { value = { for key, rule in aws_cloudwatch_event_rule.this : key => rule.arn } }
