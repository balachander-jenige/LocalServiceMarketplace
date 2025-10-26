# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = "${var.project_name}-cluster"
  role_arn = var.cluster_role_arn
  version  = var.cluster_version

  vpc_config {
    # Control plane can use both public and private subnets for HA
    subnet_ids              = concat(var.private_subnet_ids, var.public_subnet_ids)
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]
  }

  # Enable logging
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  depends_on = [
    aws_cloudwatch_log_group.cluster_logs
  ]

  tags = {
    Name    = "${var.project_name}-cluster"
    Project = var.project_name
  }
}

# CloudWatch Log Group for EKS
resource "aws_cloudwatch_log_group" "cluster_logs" {
  name              = "/aws/eks/${var.project_name}-cluster/cluster"
  retention_in_days = 7
  
  tags = {
    Name    = "${var.project_name}-cluster-logs"
    Project = var.project_name
  }
}

# EKS Node Group
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.project_name}-nodes"
  node_role_arn   = var.node_group_role_arn
  # Worker nodes ONLY in private subnets for security
  subnet_ids      = var.private_subnet_ids

  instance_types = var.instance_types
  capacity_type  = "ON_DEMAND"

  scaling_config {
    desired_size = var.desired_size
    max_size     = var.max_size
    min_size     = var.min_size
  }

  update_config {
    max_unavailable_percentage = 50
  }

  # Ensure that IAM Role permissions are created before and deleted after EKS Node Group handling.
  # Otherwise, EKS will not be able to properly delete EC2 Instances and Elastic Network Interfaces.
  depends_on = [
    aws_eks_cluster.main
  ]

  tags = {
    Name    = "${var.project_name}-nodes"
    Project = var.project_name
  }
}