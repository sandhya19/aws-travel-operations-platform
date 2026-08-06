variable "name" { type = string }
variable "trusted_services" { type = list(string) }
variable "inline_policies" {
  type    = map(string)
  default = {}
}

variable "managed_policy_arns" {
  type    = list(string)
  default = []
}

variable "tags" {
  type    = map(string)
  default = {}
}
