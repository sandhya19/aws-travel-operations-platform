variable "name" { type = string }
variable "cidr_block" { type = string }
variable "availability_zones" { type = list(string) }
variable "private_subnet_cidrs" { type = map(string) }
variable "tags" { default = {} }
