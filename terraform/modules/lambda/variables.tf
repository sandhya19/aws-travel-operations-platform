variable "function_name" { type = string }
variable "description" { type = string }
variable "role_arn" { type = string }
variable "handler" { type = string }
variable "runtime" { default = "python3.12" }
variable "package_file" { type = string }
variable "source_code_hash" { default = null }
variable "timeout" { default = 30 }
variable "memory_size" { default = 512 }
variable "kms_key_arn" { default = null }
variable "subnet_ids" { default = [] }
variable "security_group_ids" { default = [] }
variable "environment_variables" {
  type    = map(string)
  default = {}
}
variable "log_group_name" { type = string }
variable "tags" {
  type    = map(string)
  default = {}
}
