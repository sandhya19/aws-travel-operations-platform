# Example: module "db_secret" { source = "../../modules/secrets_manager" name = "travel/db" description = "Database credentials" kms_key_arn = module.kms.key_arn }
