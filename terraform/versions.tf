terraform {
  required_version = ">= 1.10.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state so GitHub Actions remembers what it created between runs.
  # bucket / key / region are passed at `terraform init` time via -backend-config.
  backend "s3" {
    use_lockfile = true # S3-native state locking (no DynamoDB table needed)
    encrypt      = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = var.project_name
      ManagedBy = "terraform"
    }
  }
}
