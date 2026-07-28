variable "name" { type = string }
variable "description" { type = string }
variable "kms_key_arn" { type = string }
variable "secret_string" { default = null }
variable "recovery_window_in_days" { default = 30 }
variable "tags" { default = {} }
