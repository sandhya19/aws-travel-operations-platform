variable "aws_region" { default = "eu-west-2" }
variable "knowledge_bucket_name" { default = "travel-operations-prod-knowledge-change-me" }
variable "cockroachdb_egress_cidrs" { default = ["0.0.0.0/0"] }
variable "cockroachdb_secret_string" { default = null }
