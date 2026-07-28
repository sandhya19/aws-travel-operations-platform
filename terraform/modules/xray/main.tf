resource "aws_xray_group" "this" {
  group_name        = var.name
  filter_expression = var.filter_expression
  tags              = var.tags
}

resource "aws_xray_sampling_rule" "this" {
  rule_name      = "${var.name}-sampling"
  priority       = var.priority
  version        = 1
  reservoir_size = var.reservoir_size
  fixed_rate     = var.fixed_rate
  url_path       = "*"
  host           = "*"
  http_method    = "*"
  service_name   = "*"
  service_type   = "*"
  resource_arn   = "*"
  attributes     = {}
}
