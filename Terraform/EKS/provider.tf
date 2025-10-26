# =============================================================================
# TERRAFORM PROVIDER CONFIGURATION
# =============================================================================
# This file configures the AWS provider and other required providers
terraform {
  required_version = ">= 1.4.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region  = "ap-southeast-1"  # Change to your desired AWS region
  access_key = "AKIAX3MB7W5PIG4IBB4M"  # Replace with your access key
  secret_key = "Fu/rjftt7DLPCvKq/fBcrqLuvHMHK1E8ZhWakWRl"  # Replace with your secret key
}

  # Uncomment and configure backend for remote state storage
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "freelancer-marketplace/terraform.tfstate"
  #   region         = "ap-southeast-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-locks"
  # }


# -----------------------------------------------------------------------------
# AWS PROVIDER CONFIGURATION
# -----------------------------------------------------------------------------
# Configure the AWS Provider with your region

