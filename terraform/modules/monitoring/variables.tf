variable "name" { type = string }
variable "retention_in_days" { default = 30 }
variable "kms_key_arn" { default = null }
variable "tags" { default = {} }
