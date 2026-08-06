variable "name" { type = string }
variable "rules" {
  type = map(object({
    event_pattern                = optional(string)
    schedule_expression          = optional(string)
    target_arn                   = string
    dlq_arn                      = string
    maximum_event_age_in_seconds = number
    maximum_retry_attempts       = number
    role_arn                     = optional(string)
  }))
  default = {}
}
variable "tags" { default = {} }
