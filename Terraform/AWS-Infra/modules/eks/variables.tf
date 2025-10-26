variable "cluster_role_arn" {
  description = "ARN of the IAM role for EKS cluster"
  type        = string
}

variable "node_group_role_arn" {
  description = "ARN of the IAM role for EKS node group"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where EKS cluster will be created"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for EKS worker nodes"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for EKS control plane"
  type        = list(string)
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

# EKS Configuration - with sensible defaults
variable "cluster_version" {
  description = "Kubernetes version for the EKS cluster"
  type        = string
  default     = "1.29"
}

variable "instance_types" {
  description = "Instance types for the EKS node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "desired_size" {
  description = "Desired number of nodes in the node group"
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum number of nodes in the node group"
  type        = number
  default     = 4
}

variable "min_size" {
  description = "Minimum number of nodes in the node group"
  type        = number
  default     = 1
}