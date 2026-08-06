variable "name" { type = string }
variable "description" { type = string }
variable "stage_name" { default = "$default" }
variable "access_log_group_arn" { type = string }
variable "access_log_format" { default = "{\"requestId\":\"$context.requestId\"}" }
variable "routes" {
  type    = map(object({ route_key = string, invoke_arn = string, function_name = string }))
  default = {}
}
variable "tags" { default = {} }
