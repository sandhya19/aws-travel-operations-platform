# Example: module "workflow_queue" { source = "../../modules/sqs" name = "travel-dev-workflow" kms_key_arn = module.kms.key_arn }
