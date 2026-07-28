variable "name" { type = string }
variable "description" { type = string }
variable "blocked_input_messaging" { default = "The request could not be processed safely." }
variable "blocked_outputs_messaging" { default = "The response could not be produced safely." }
variable "tags" { default = {} }
