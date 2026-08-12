output "vpc_id" { value = module.network.vpc_id }
output "private_subnet_ids" { value = module.network.private_subnet_ids }
output "travel_api_endpoint" { value = module.api.api_endpoint }
output "travel_event_bus_name" { value = module.events.event_bus_name }
output "agentcore_runtime_arn" {
  description = "ARN used with the Bedrock AgentCore Runtime invocation API."
  value       = aws_bedrockagentcore_agent_runtime.travel_operations.agent_runtime_arn
}

output "operations_alert_topic_arn" {
  description = "SNS topic used by CloudWatch operational alarms."
  value       = module.operations_alerts.topic_arn
}

output "operations_dashboard_name" {
  description = "CloudWatch dashboard containing workflow, API, DLQ, and KMS operational signals."
  value       = aws_cloudwatch_dashboard.operations.dashboard_name
}
