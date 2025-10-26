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
