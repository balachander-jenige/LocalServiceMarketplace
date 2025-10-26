# =============================================================================
# SUBNET TAGS FOR EKS DISCOVERY
# =============================================================================
# Add required tags to existing subnets for EKS to properly discover and use them

# Tag private subnets for EKS internal load balancers
resource "aws_ec2_tag" "private_subnet_cluster_tag" {
  for_each    = toset(var.private_subnet_ids)
  resource_id = each.value
  key         = "kubernetes.io/cluster/${var.cluster_name}"
  value       = "owned"
}

resource "aws_ec2_tag" "private_subnet_elb_tag" {
  for_each    = toset(var.private_subnet_ids)
  resource_id = each.value
  key         = "kubernetes.io/role/internal-elb"
  value       = "1"
}

# Tag public subnets for EKS external load balancers
resource "aws_ec2_tag" "public_subnet_cluster_tag" {
  for_each    = toset(var.public_subnet_ids)
  resource_id = each.value
  key         = "kubernetes.io/cluster/${var.cluster_name}"
  value       = "shared"
}

resource "aws_ec2_tag" "public_subnet_elb_tag" {
  for_each    = toset(var.public_subnet_ids)
  resource_id = each.value
  key         = "kubernetes.io/role/elb"
  value       = "1"
}