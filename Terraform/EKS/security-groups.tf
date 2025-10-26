# =============================================================================
# SECURITY GROUPS FOR NEW EKS CLUSTER
# =============================================================================
# This file creates security groups for the NEW EKS cluster in private subnets

# -----------------------------------------------------------------------------
# 1. EKS CLUSTER SECURITY GROUP
# -----------------------------------------------------------------------------
# Controls traffic to/from the EKS control plane

resource "aws_security_group" "eks_cluster" {
  name_prefix = "${var.cluster_name}-cluster-"
  description = "Security group for EKS cluster control plane"
  vpc_id      = var.vpc_id

  # Allow HTTPS communication with the cluster API server
  ingress {
    description = "HTTPS from everywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-cluster-sg"
  }
}

# -----------------------------------------------------------------------------
# 2. EKS WORKER NODES SECURITY GROUP
# -----------------------------------------------------------------------------
# Controls traffic to/from EKS worker nodes in private subnets

resource "aws_security_group" "eks_nodes" {
  name_prefix = "${var.cluster_name}-nodes-"
  description = "Security group for EKS worker nodes"
  vpc_id      = var.vpc_id

  # Allow nodes to communicate with each other
  ingress {
    description = "Node to node communication"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    self        = true
  }

  # Allow worker Kubelets and pods to receive communication from the cluster control plane
  ingress {
    description     = "Communication from cluster control plane"
    from_port       = 1025
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
  }

  # Allow pods running extension API servers on port 443 to receive communication from cluster control plane
  ingress {
    description     = "HTTPS from cluster control plane"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
  }

  # ALB to EKS nodes rule will be added as separate resource to avoid circular dependency

  # Allow all outbound traffic
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-nodes-sg"
  }
}

# -----------------------------------------------------------------------------
# 3. APPLICATION LOAD BALANCER SECURITY GROUP
# -----------------------------------------------------------------------------
# Controls traffic from internet to ALB (in public subnets)

resource "aws_security_group" "alb" {
  name_prefix = "${var.cluster_name}-alb-"
  description = "Security group for Application Load Balancer"
  vpc_id      = var.vpc_id

  # Allow HTTP traffic from internet
  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # Allow HTTPS traffic from internet
  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  # Outbound to EKS nodes rule will be added as separate resource to avoid circular dependency

  # Allow outbound HTTPS for health checks
  egress {
    description = "HTTPS outbound"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-alb-sg"
  }
}

# -----------------------------------------------------------------------------
# 4. SECURITY GROUP RULES FOR CLUSTER COMMUNICATION
# -----------------------------------------------------------------------------
# Additional rules to allow EKS cluster and nodes to communicate

# HTTPS ingress rule already exists inline in aws_security_group.eks_cluster above

resource "aws_security_group_rule" "cluster_egress_node_https" {
  description              = "Allow cluster control plane to communicate with worker nodes"
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.eks_nodes.id
  security_group_id        = aws_security_group.eks_cluster.id
}

resource "aws_security_group_rule" "cluster_egress_node_kubelet" {
  description              = "Allow cluster control plane to communicate with worker node kubelet"
  type                     = "egress"
  from_port                = 10250
  to_port                  = 10250
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.eks_nodes.id
  security_group_id        = aws_security_group.eks_cluster.id
}

# -----------------------------------------------------------------------------
# 5. ALB ↔ EKS NODES CROSS-REFERENCE RULES (SEPARATE TO AVOID CYCLES)
# -----------------------------------------------------------------------------
# These rules enable ALB to reach EKS services via NodePort (30000-32767)
# This supports Kubernetes Ingress with target-type: instance
# For target-type: ip, additional rules for pod CIDR ranges would be needed

resource "aws_security_group_rule" "alb_to_eks_nodes" {
  description              = "Allow ALB to reach EKS pods via NodePort"
  type                     = "egress"
  from_port                = 30000
  to_port                  = 32767
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.eks_nodes.id
  security_group_id        = aws_security_group.alb.id
}

resource "aws_security_group_rule" "eks_nodes_from_alb" {
  description              = "Allow EKS nodes to receive traffic from ALB"
  type                     = "ingress"
  from_port                = 30000
  to_port                  = 32767
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.alb.id
  security_group_id        = aws_security_group.eks_nodes.id
}