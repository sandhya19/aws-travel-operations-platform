variable "name" { type = string }
variable "role_arn" { type = string }
variable "definition" { type = string }
variable "log_group_arn" { type = string }
variable "type" { default = "STANDARD" }
variable "log_level" { default = "ALL" }
variable "tags" { default = {} }
