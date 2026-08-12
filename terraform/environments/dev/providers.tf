terraform {
  backend "s3" {
    bucket         = "travel-operations-terraform-state-489922706678-eu-west-2"
    key            = "dev/terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "travel-operations-terraform-locks"
    encrypt        = true
    kms_key_id     = "alias/travel-operations-terraform-state"
    profile        = "AdministratorAccess-489922706678"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags { tags = local.tags }
}

locals {
  name = "${var.project_name}-${var.environment}"
  tags = { Project = var.project_name, Environment = var.environment, ManagedBy = "Terraform" }
}
