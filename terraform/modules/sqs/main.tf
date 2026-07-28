resource "aws_sqs_queue" "dlq" {
  name                      = "${var.name}-dlq"
  message_retention_seconds = var.dlq_message_retention_seconds
  kms_master_key_id         = var.kms_key_arn
  sqs_managed_sse_enabled   = var.kms_key_arn == null
  tags                      = var.tags
}

resource "aws_sqs_queue" "this" {
  name                       = var.name
  visibility_timeout_seconds = var.visibility_timeout_seconds
  message_retention_seconds  = var.message_retention_seconds
  receive_wait_time_seconds  = var.receive_wait_time_seconds
  kms_master_key_id          = var.kms_key_arn
  sqs_managed_sse_enabled    = var.kms_key_arn == null
  redrive_policy             = jsonencode({ deadLetterTargetArn = aws_sqs_queue.dlq.arn, maxReceiveCount = var.max_receive_count })
  tags                       = var.tags
}
