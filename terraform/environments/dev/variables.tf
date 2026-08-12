variable "aws_region" { default = "eu-west-2" }
variable "project_name" { default = "travel-operations" }
variable "environment" { default = "dev" }
variable "vpc_cidr" { default = "10.20.0.0/16" }
variable "availability_zones" { default = ["eu-west-2a", "eu-west-2b"] }
variable "private_subnet_cidrs" { default = { a = "10.20.1.0/24", b = "10.20.2.0/24" } }
variable "cockroachdb_egress_cidrs" { default = ["0.0.0.0/0"] }
variable "knowledge_bucket_name" {
  type        = string
  description = "Globally unique private S3 bucket for tenant-prefixed approved PDF sources."
}
variable "cockroachdb_secret_string" { default = null }
variable "database_url" {
  type      = string
  sensitive = true
}

variable "jwt_secret" {
  type      = string
  sensitive = true
}

variable "cockroach_root_cert_pem" {
  type      = string
  sensitive = true
}

variable "api_package_file" {
  type    = string
  default = "../../../dist/travel-operations-api.zip"
}

variable "simulate_approval_callback_failure" {
  type        = bool
  default     = false
  description = "Dev-only recovery-drill switch; fails after approval persistence before Step Functions callback."
}

variable "memory_retention_days" {
  type        = number
  default     = 365
  description = "Number of days terminal travel-case memory remains active before expiry."
}

variable "agent_runtime_package_file" {
  type        = string
  default     = "../../../dist/travel-operations-agent-runtime.zip"
  description = "AgentCore Runtime ZIP package produced by scripts/build_agent_runtime_package.py."
}

variable "operations_alert_email" {
  type        = string
  default     = null
  nullable    = true
  description = "Optional email address that receives dev operations alarms after SNS confirmation."
}
