variable "name" { type = string }
variable "vpc_id" { type = string }
variable "allowed_egress_cidrs" { type = list(string) }
variable "connection_secret_arn" { type = string }
variable "tags" { default = {} }
