resource "aws_secretsmanager_secret" "this" {
  name                    = var.name
  description             = var.description
  kms_key_id              = var.kms_key_arn
  recovery_window_in_days = var.recovery_window_in_days
  tags                    = var.tags
}

resource "aws_secretsmanager_secret_version" "initial" {
  count         = var.secret_string == null ? 0 : 1
  secret_id     = aws_secretsmanager_secret.this.id
  secret_string = var.secret_string
}
