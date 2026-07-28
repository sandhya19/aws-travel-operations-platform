resource "aws_bedrock_guardrail" "this" {
  name                      = var.name
  blocked_input_messaging   = var.blocked_input_messaging
  blocked_outputs_messaging = var.blocked_outputs_messaging
  description               = var.description
  tags                      = var.tags
}
