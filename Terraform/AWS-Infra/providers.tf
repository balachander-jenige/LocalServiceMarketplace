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