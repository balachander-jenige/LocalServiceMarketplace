# =============================================================================
# OUTPUTS FOR NEW EKS CLUSTER INFRASTRUCTURE
# =============================================================================
# This file defines outputs for the newly created EKS cluster

# -----------------------------------------------------------------------------
# EKS CLUSTER INFORMATION
# -----------------------------------------------------------------------------

output "cluster_id" {
  description = "EKS cluster ID"
  value       = aws_eks_cluster.main.cluster_id
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "cluster_arn" {
  description = "EKS cluster ARN"
  value       = aws_eks_cluster.main.arn
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_version" {
  description = "EKS cluster Kubernetes version"
  value       = aws_eks_cluster.main.version
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = aws_security_group.eks_cluster.id
}

# -----------------------------------------------------------------------------
# NODE GROUP INFORMATION
# -----------------------------------------------------------------------------

output "node_group_arn" {
  description = "EKS node group ARN"
  value       = aws_eks_node_group.main.arn
}

output "node_group_status" {
  description = "EKS node group status"
  value       = aws_eks_node_group.main.status
}

output "eks_nodes_security_group_id" {
  description = "Security group ID for EKS worker nodes"
  value       = aws_security_group.eks_nodes.id
}

# -----------------------------------------------------------------------------
# LOAD BALANCER INFORMATION
# -----------------------------------------------------------------------------

output "alb_security_group_id" {
  description = "Security group ID for Application Load Balancer"
  value       = aws_security_group.alb.id
}

# ALB access logs output removed - S3 bucket creation disabled

# -----------------------------------------------------------------------------
# IAM ROLES
# -----------------------------------------------------------------------------

output "cluster_iam_role_arn" {
  description = "IAM role ARN of the EKS cluster (either provided or created)"
  value       = var.cluster_iam_role_arn != "" ? var.cluster_iam_role_arn : try(aws_iam_role.eks_cluster_role[0].arn, "")
}

output "node_group_iam_role_arn" {
  description = "IAM role ARN of the EKS node group (either provided or created)"
  value       = var.node_group_iam_role_arn != "" ? var.node_group_iam_role_arn : try(aws_iam_role.eks_node_group_role[0].arn, "")
}

output "aws_load_balancer_controller_role_arn" {
  description = "IAM role ARN for AWS Load Balancer Controller"
  value       = aws_iam_role.aws_load_balancer_controller.arn
}

# -----------------------------------------------------------------------------
# OIDC PROVIDER
# -----------------------------------------------------------------------------

output "oidc_provider_arn" {
  description = "OIDC Provider ARN for EKS cluster"
  value       = aws_iam_openid_connect_provider.eks.arn
}

# -----------------------------------------------------------------------------
# CERTIFICATE INFORMATION
# -----------------------------------------------------------------------------

output "certificate_arn" {
  description = "ARN of the ACM certificate"
  value       = var.create_certificate && var.domain_name != "" ? aws_acm_certificate.main[0].arn : null
}

# -----------------------------------------------------------------------------
# KUBERNETES INGRESS CONFIGURATION
# -----------------------------------------------------------------------------

output "ingress_annotations" {
  description = "Annotations for Kubernetes ingress (ALB configuration)"
  value = {
    "kubernetes.io/ingress.class"                    = "alb"
    "alb.ingress.kubernetes.io/scheme"               = "internet-facing"
    "alb.ingress.kubernetes.io/target-type"         = "ip"
    "alb.ingress.kubernetes.io/security-groups"     = aws_security_group.alb.id
    "alb.ingress.kubernetes.io/subnets"             = join(",", var.public_subnet_ids)
    "alb.ingress.kubernetes.io/listen-ports"        = "[{\"HTTP\": 80}, {\"HTTPS\": 443}]"
    "alb.ingress.kubernetes.io/ssl-policy"          = "ELBSecurityPolicy-TLS-1-2-Ext-2018-06"
    "alb.ingress.kubernetes.io/certificate-arn"     = var.create_certificate && var.domain_name != "" ? aws_acm_certificate.main[0].arn : ""
    "alb.ingress.kubernetes.io/ssl-redirect"        = "443"
    "alb.ingress.kubernetes.io/load-balancer-name"  = "${var.cluster_name}-alb"
  }
}

# -----------------------------------------------------------------------------
# CONNECTION COMMANDS
# -----------------------------------------------------------------------------

output "kubectl_config_command" {
  description = "Command to configure kubectl for this cluster"
  value       = "aws eks update-kubeconfig --region ${var.region} --name ${aws_eks_cluster.main.name}"
}

output "cluster_info" {
  description = "Useful cluster information"
  value = {
    cluster_name         = aws_eks_cluster.main.name
    cluster_endpoint     = aws_eks_cluster.main.endpoint
    cluster_version      = aws_eks_cluster.main.version
    private_subnets      = var.private_subnet_ids
    public_subnets       = var.public_subnet_ids
    vpc_id              = var.vpc_id
    region              = var.region
  }
}

# -----------------------------------------------------------------------------
# APPLICATION LOAD BALANCER OUTPUTS
# -----------------------------------------------------------------------------

output "alb_arn" {
  description = "Application Load Balancer ARN"
  value       = aws_lb.main.arn
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Application Load Balancer hosted zone ID"
  value       = aws_lb.main.zone_id
}

output "alb_target_group_arn" {
  description = "ALB target group ARN for EKS services"
  value       = aws_lb_target_group.eks_services.arn
}

# -----------------------------------------------------------------------------
# DIAGNOSTIC OUTPUTS FOR TROUBLESHOOTING
# -----------------------------------------------------------------------------

output "private_subnet_route_tables" {
  description = "Route tables associated with private subnets"
  value = {
    for k, v in data.aws_route_table.private : k => {
      route_table_id = v.id
      routes         = v.routes
    }
  }
}

output "nat_gateways" {
  description = "NAT Gateways in VPC (for diagnostics)"
  value = {
    available_nat_gateways = data.aws_nat_gateways.existing.ids
  }
}

# -----------------------------------------------------------------------------
# AWS LOAD BALANCER CONTROLLER INFORMATION
# -----------------------------------------------------------------------------

output "aws_load_balancer_controller_role_arn" {
  description = "ARN of the AWS Load Balancer Controller IAM role"
  value       = aws_iam_role.aws_load_balancer_controller.arn
}

output "aws_load_balancer_controller_policy_arn" {
  description = "ARN of the AWS Load Balancer Controller IAM policy"
  value       = aws_iam_policy.aws_load_balancer_controller.arn
}

output "oidc_provider_arn" {
  description = "ARN of the EKS OIDC provider for service account authentication"
  value       = aws_iam_openid_connect_provider.eks.arn
}

# -----------------------------------------------------------------------------
# POST-DEPLOYMENT COMMANDS
# -----------------------------------------------------------------------------

output "kubectl_config_command" {
  description = "Command to configure kubectl"
  value       = "aws eks update-kubeconfig --region ${data.aws_region.current.name} --name ${aws_eks_cluster.main.name}"
}

output "load_balancer_controller_helm_command" {
  description = "Helm command to install AWS Load Balancer Controller"
  value = "helm install aws-load-balancer-controller eks/aws-load-balancer-controller -n kube-system --set clusterName=${aws_eks_cluster.main.name} --set serviceAccount.annotations.'eks\\.amazonaws\\.com/role-arn'=${aws_iam_role.aws_load_balancer_controller.arn} --set region=${data.aws_region.current.name} --set vpcId=${var.vpc_id}"
}