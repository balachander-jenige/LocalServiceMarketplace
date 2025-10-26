# =============================================================================
# TERRAFORM VARIABLES FOR FREELANCER MARKETPLACE INFRASTRUCTURE
# =============================================================================
# This file defines all the input variables needed to create the infrastructure
# that matches your existing EKS deployment setup

# -----------------------------------------------------------------------------
# BASIC PROJECT CONFIGURATION
# -----------------------------------------------------------------------------

variable "project_name" {
  description = "Name of the project - used for tagging and naming resources"
  type        = string
  default     = "freelancer-marketplace"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "production"
}

variable "region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "ap-southeast-1"
}

# -----------------------------------------------------------------------------
# EXISTING NETWORK INFRASTRUCTURE
# -----------------------------------------------------------------------------
# These should match your current EKS cluster network setup

variable "vpc_id" {
  description = "ID of the existing VPC where EKS cluster is deployed"
  type        = string
  # Example: "vpc-07e46d9a4ad5924c2"
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs where ALB will be deployed"
  type        = list(string)
  # Example: ["subnet-03f7274e3abb4833c", "subnet-0f211af0306368c36"]
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs where NEW EKS cluster will be created"
  type        = list(string)
  # Example: ["subnet-xxx", "subnet-yyy"] - these must be PRIVATE subnets
  # If you don't have private subnets, you'll need to create them first
}

# -----------------------------------------------------------------------------
# NEW EKS CLUSTER CONFIGURATION
# -----------------------------------------------------------------------------
# Configuration for the NEW EKS cluster to be created

variable "cluster_name" {
  description = "Name for the NEW EKS cluster to be created"
  type        = string
  default     = "freelancer-marketplace-eks"
}

variable "cluster_version" {
  description = "Kubernetes version for the new EKS cluster"
  type        = string
  default     = "1.33"  # Use a stable version
}

variable "node_group_instance_types" {
  description = "Instance types for EKS managed node group"
  type        = list(string)
  default     = ["t3.medium", "t3.large"]
}

variable "node_group_scaling_config" {
  description = "Scaling configuration for EKS node group"
  type = object({
    desired_size = number
    max_size     = number
    min_size     = number
  })
  default = {
    desired_size = 2
    max_size     = 5
    min_size     = 1
  }
}

# -----------------------------------------------------------------------------
# APPLICATION LOAD BALANCER CONFIGURATION
# -----------------------------------------------------------------------------
# Settings for the ALB that will be created by Kubernetes ingress

variable "enable_deletion_protection" {
  description = "Enable deletion protection for the ALB"
  type        = bool
  default     = false
}

# ALB access logs variables removed - S3 bucket creation disabled

# -----------------------------------------------------------------------------
# NOTE: DATABASE ENDPOINTS NOT NEEDED IN TERRAFORM
# -----------------------------------------------------------------------------
# Since you're using existing managed databases and referencing them directly
# in your Kubernetes secrets, no database variables are needed in Terraform.

# -----------------------------------------------------------------------------
# CERTIFICATE CONFIGURATION
# -----------------------------------------------------------------------------
# SSL certificate settings for HTTPS

variable "domain_name" {
  description = "Domain name for SSL certificate (leave empty for ALB default certificate)"
  type        = string
  default     = ""
}

variable "create_certificate" {
  description = "Whether to create ACM certificate for custom domain"
  type        = bool
  default     = false
}

variable "subject_alternative_names" {
  description = "Additional domain names for the SSL certificate"
  type        = list(string)
  default     = []
}

# -----------------------------------------------------------------------------
# SECURITY CONFIGURATION
# -----------------------------------------------------------------------------
# Security settings for the infrastructure

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the ALB from internet"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Allow all - restrict this for production
}



# -----------------------------------------------------------------------------
# NOTE: MICROSERVICE PORT CONFIGURATION NOT NEEDED
# -----------------------------------------------------------------------------
# The new EKS configuration uses simplified security groups that allow
# traffic on the standard Kubernetes NodePort range (30000-32767).
# Individual microservice ports are handled by Kubernetes services and ingress,
# not by Terraform security group rules.



# -----------------------------------------------------------------------------
# OPTIONAL: Use existing IAM role ARNs instead of creating new ones
# -----------------------------------------------------------------------------
variable "cluster_iam_role_arn" {
  description = "Optional: ARN of an existing IAM role to use for the EKS cluster (if provided, Terraform will not create a new cluster role)"
  type        = string
  default     = ""
}

variable "node_group_iam_role_arn" {
  description = "Optional: ARN of an existing IAM role to use for the EKS node group (if provided, Terraform will not create a new node group role)"
  type        = string
  default     = ""
}
