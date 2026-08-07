variable "aws_region" { default = "eu-west-2" }
variable "project_name" { default = "travel-operations" }
variable "environment" { default = "prod" }
variable "vpc_cidr" { default = "10.40.0.0/16" }
variable "availability_zones" { default = ["eu-west-2a", "eu-west-2b"] }
variable "private_subnet_cidrs" { default = { a = "10.40.1.0/24", b = "10.40.2.0/24" } }
variable "knowledge_bucket_name" { default = "travel-operations-prod-knowledge-change-me" }
variable "cockroachdb_egress_cidrs" { default = ["0.0.0.0/0"] }
variable "cockroachdb_secret_string" { default = null }
