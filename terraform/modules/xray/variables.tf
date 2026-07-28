variable "name" { type = string }
variable "filter_expression" { default = "service(*)" }
variable "priority" { default = 9000 }
variable "reservoir_size" { default = 1 }
variable "fixed_rate" { default = 0.1 }
variable "tags" { default = {} }
