resource "aws_security_group" "egress" {
  name        = "${var.name}-cockroach-egress"
  description = "Controlled egress from Lambda functions to CockroachDB"
  vpc_id      = var.vpc_id

  egress {
    description = "TLS to CockroachDB Serverless"
    from_port   = 26257
    to_port     = 26257
    protocol    = "tcp"
    cidr_blocks = var.allowed_egress_cidrs
  }

  tags = var.tags
}
