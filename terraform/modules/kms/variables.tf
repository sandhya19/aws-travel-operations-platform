variable "alias" { type = string }
variable "description" { type = string }
variable "deletion_window_in_days" { default = 30 }
variable "policy" { default = null }
variable "tags" { default = {} }
