resource "aws_cloudwatch_event_bus" "this" {
  name = var.name
  tags = var.tags
}

resource "aws_cloudwatch_event_rule" "this" {
  for_each            = var.rules
  name                = "${var.name}-${each.key}"
  event_bus_name      = aws_cloudwatch_event_bus.this.name
  event_pattern       = try(each.value.event_pattern, null)
  schedule_expression = try(each.value.schedule_expression, null)
  tags                = var.tags
}

resource "aws_cloudwatch_event_target" "this" {
  for_each       = var.rules
  rule           = aws_cloudwatch_event_rule.this[each.key].name
  event_bus_name = aws_cloudwatch_event_bus.this.name
  arn            = each.value.target_arn
  target_id      = each.key
  role_arn       = each.value.role_arn
  retry_policy {
    maximum_event_age_in_seconds = each.value.maximum_event_age_in_seconds
    maximum_retry_attempts       = each.value.maximum_retry_attempts
  }
  dead_letter_config { arn = each.value.dlq_arn }
}
