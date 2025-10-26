# =============================================================================
# MAIN INFRASTRUCTURE FOR NEW EKS CLUSTER
# =============================================================================
# This file creates a NEW EKS cluster in private subnets with ALB in public subnets


# Current AWS region
data "aws_region" "current" {}

# VPC information
data "aws_vpc" "existing" {
  id = var.vpc_id
}

# Existing subnets
data "aws_subnets" "public" {
  filter {
    name   = "subnet-id"
    values = var.public_subnet_ids
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "subnet-id"
    values = var.private_subnet_ids
  }
}

# Get availability zones for the subnets
data "aws_subnet" "private" {
  for_each = toset(var.private_subnet_ids)
  id       = each.value
}

data "aws_subnet" "public" {
  for_each = toset(var.public_subnet_ids)
  id       = each.value
}

# Check route tables for private subnets
data "aws_route_table" "private" {
  for_each  = toset(var.private_subnet_ids)
  subnet_id = each.value
}

# Check if NAT Gateway exists in route tables (optional - for diagnostics)
data "aws_nat_gateways" "existing" {
  vpc_id = var.vpc_id
  
  filter {
    name   = "state"
    values = ["available"]
  }
}

# Current AWS caller identity
data "aws_caller_identity" "current" {}

# -----------------------------------------------------------------------------
# EKS CLUSTER IAM ROLE
# -----------------------------------------------------------------------------
locals {
  eks_cluster_role_arn = var.cluster_iam_role_arn != "" ? var.cluster_iam_role_arn : try(aws_iam_role.eks_cluster_role[0].arn, "")
  eks_node_group_role_arn = var.node_group_iam_role_arn != "" ? var.node_group_iam_role_arn : try(aws_iam_role.eks_node_group_role[0].arn, "")
}

# Create cluster role only if user did not provide an ARN
resource "aws_iam_role" "eks_cluster_role" {
  count = var.cluster_iam_role_arn == "" ? 1 : 0

  name = "${var.cluster_name}-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.cluster_name}-cluster-role"
  }
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  count      = var.cluster_iam_role_arn == "" ? 1 : 0
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster_role[0].name
}

# -----------------------------------------------------------------------------
# EKS NODE GROUP IAM ROLE
# -----------------------------------------------------------------------------

resource "aws_iam_role" "eks_node_group_role" {
  count = var.node_group_iam_role_arn == "" ? 1 : 0

  name = "${var.cluster_name}-node-group-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.cluster_name}-node-group-role"
  }
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  count      = var.node_group_iam_role_arn == "" ? 1 : 0
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node_group_role[0].name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  count      = var.node_group_iam_role_arn == "" ? 1 : 0
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node_group_role[0].name
}

resource "aws_iam_role_policy_attachment" "eks_container_registry_policy" {
  count      = var.node_group_iam_role_arn == "" ? 1 : 0
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_node_group_role[0].name
}

# -----------------------------------------------------------------------------
# EKS CLUSTER
# -----------------------------------------------------------------------------

resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = local.eks_cluster_role_arn
  version  = var.cluster_version

  vpc_config {
    subnet_ids              = var.private_subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]
    security_group_ids      = [aws_security_group.eks_cluster.id]
  }

  # Enable EKS cluster logging
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_security_group.eks_cluster
  ]

  tags = {
    Name = var.cluster_name
  }
}

# -----------------------------------------------------------------------------
# EKS NODE GROUP
# -----------------------------------------------------------------------------

resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-nodes"
  node_role_arn   = local.eks_node_group_role_arn
  subnet_ids      = var.private_subnet_ids  # CRITICAL: This forces nodes into private subnets
  instance_types  = var.node_group_instance_types

  # Use EKS managed configuration (no launch template)
  ami_type       = "AL2023_x86_64_STANDARD"  # Amazon Linux 2023 supports newer K8s versions
  capacity_type  = "ON_DEMAND"
  disk_size      = 20

  scaling_config {
    desired_size = var.node_group_scaling_config.desired_size
    max_size     = var.node_group_scaling_config.max_size
    min_size     = var.node_group_scaling_config.min_size
  }

  update_config {
    max_unavailable = 1
  }

  # Ensure that IAM Role permissions are created before and deleted after EKS Node Group handling.
  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy,
    aws_security_group.eks_nodes,
    # Wait for subnet tags to be applied
    aws_ec2_tag.private_subnet_cluster_tag,
    aws_ec2_tag.private_subnet_elb_tag
  ]

  tags = {
    Name                                        = "${var.cluster_name}-nodes"
    "kubernetes.io/cluster/${var.cluster_name}" = "owned"
  }

  lifecycle {
    ignore_changes = [scaling_config[0].desired_size]
  }
}

# -----------------------------------------------------------------------------
# AWS Load Balancer Controller IAM Role
# -----------------------------------------------------------------------------
# NOTE: This IAM policy has been updated to resolve common permission issues:
# 1. Added elasticloadbalancing:DescribeListenerAttributes permission
# 2. Removed restrictive conditions on AddTags/RemoveTags actions
# 3. This policy supports both IP and instance target types for ALB ingress

data "aws_iam_policy_document" "aws_load_balancer_controller_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${replace(aws_eks_cluster.main.identity[0].oidc[0].issuer, "https://", "")}:sub"
      values   = ["system:serviceaccount:kube-system:aws-load-balancer-controller"]
    }

    principals {
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "aws_load_balancer_controller" {
  assume_role_policy = data.aws_iam_policy_document.aws_load_balancer_controller_assume_role_policy.json
  name               = "${var.cluster_name}-aws-load-balancer-controller"
  tags = {
    Name = "${var.cluster_name}-aws-load-balancer-controller"
  }
}

resource "aws_iam_policy" "aws_load_balancer_controller" {
  policy = file("${path.module}/iam-policies/AWSLoadBalancerController.json")
  name   = "${var.cluster_name}-AWSLoadBalancerController"
  tags = {
    Name = "${var.cluster_name}-AWSLoadBalancerController"
  }
}

resource "aws_iam_role_policy_attachment" "aws_load_balancer_controller" {
  policy_arn = aws_iam_policy.aws_load_balancer_controller.arn
  role       = aws_iam_role.aws_load_balancer_controller.name
}

# -----------------------------------------------------------------------------
# EKS OIDC Identity Provider
# -----------------------------------------------------------------------------

data "tls_certificate" "eks" {
  url = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.main.identity[0].oidc[0].issuer

  tags = {
    Name = "${var.cluster_name}-eks-irsa"
  }
}

# -----------------------------------------------------------------------------
# S3 BUCKET FOR ALB ACCESS LOGS - REMOVED
# -----------------------------------------------------------------------------
# ALB access logging has been disabled to simplify the setup.
# If you need access logs later, you can enable them by setting:
# enable_access_logs = true in terraform.tfvars