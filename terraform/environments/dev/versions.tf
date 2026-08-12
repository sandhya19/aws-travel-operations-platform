terraform {
  required_version = ">= 1.7.0, < 2.0.0"

  required_providers {
    aws = {
      source = "hashicorp/aws"
      # AgentCore Runtime support is available in AWS provider v6.33 and later.
      version = ">= 6.33, < 7.0"
    }
  }
}
