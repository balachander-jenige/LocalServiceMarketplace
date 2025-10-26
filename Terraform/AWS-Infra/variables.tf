variable "project" {
  type        = string
  description = "Project name"
  default     = "localfreelancermarketplace"
}

variable "aws_region" {
  description = "AWS region to create resources in"
  type        = string
  default     = "ap-southeast-1"
}

variable "eks_cluster_role_name" {
  description = "Name of the EKS Cluster IAM Role"
  type        = string
  default     = "eks-cluster-role"
}

variable "eks_node_role_name" {
  description = "Name of the EKS Node IAM Role"
  type        = string
  default     = "eks-node-role"
}

# VPC Configuration
variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  type        = list(string)
  description = "List of CIDR blocks for public subnets"
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
  type        = list(string)
  description = "List of CIDR blocks for private subnets"
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}
