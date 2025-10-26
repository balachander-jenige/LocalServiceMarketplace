variable "project" {
  description = "Project or environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnets" {
  description = "List of public subnet IDs for ALB"
  type        = list(string)
}

variable "target_type" {
  description = "Target type for ALB (instance or ip)"
  type        = string
  default     = "instance"
}
