# Example: module "documents" { source = "../../modules/s3" name = "travel-dev-documents-unique" kms_key_arn = module.kms.key_arn }
