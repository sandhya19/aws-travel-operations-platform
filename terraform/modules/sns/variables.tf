variable "name" { type = string }
variable "kms_key_arn" { default = null }
variable "subscriptions" { default = {} }
variable "tags" { default = {} }
