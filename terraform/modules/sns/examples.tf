# Example: module "notifications" { source = "../../modules/sns" name = "travel-dev-notifications" kms_key_arn = module.kms.key_arn }
