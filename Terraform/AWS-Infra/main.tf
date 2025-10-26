module "vpc" {
  source          = "./modules/vpc"
  vpc_cidr        = var.vpc_cidr
  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets
}

module "iam" {
  source                = "./modules/iam"
  aws_region            = var.aws_region
  eks_cluster_role_name = var.eks_cluster_role_name
  eks_node_role_name    = var.eks_node_role_name
}

module "eks" {
  source = "./modules/eks"
  
  # Pass only essential inputs - let EKS module handle the config
  cluster_role_arn    = module.iam.eks_cluster_role_arn
  node_group_role_arn = module.iam.eks_node_role_arn
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnets
  public_subnet_ids   = module.vpc.public_subnets
  
  # Basic configuration
  project_name        = var.project
}

module "alb" {
  source         = "./modules/alb"
  project        = var.project
  vpc_id         = module.vpc.vpc_id
  public_subnets = module.vpc.public_subnets
  target_type    = "ip"
}
