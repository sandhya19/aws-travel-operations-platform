variable "name" { type = string }
variable "trusted_services" { type = list(string) }
variable "inline_policies" { default = {} }
variable "managed_policy_arns" { default = [] }
variable "tags" { default = {} }
