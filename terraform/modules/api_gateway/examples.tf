# Example: module "api" { source = "../../modules/api_gateway" name = "travel-dev" description = "Travel API" access_log_group_arn = module.api_logs.log_group_arn }
