variable "name" { type = string }
variable "kms_key_arn" { default = null }
variable "visibility_timeout_seconds" { default = 120 }
variable "message_retention_seconds" { default = 345600 }
variable "dlq_message_retention_seconds" { default = 1209600 }
variable "receive_wait_time_seconds" { default = 20 }
variable "max_receive_count" { default = 5 }
variable "tags" { default = {} }
