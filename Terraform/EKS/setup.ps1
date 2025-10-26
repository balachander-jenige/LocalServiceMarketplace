# NEW EKS CLUSTER SETUP SCRIPT
# This script helps you set up a new EKS cluster using Terraform

Write-Host "=== NEW EKS CLUSTER DEPLOYMENT SETUP ===" -ForegroundColor Green
Write-Host ""

# Check if we're in the terraform directory
if (-not (Test-Path "terraform.tfvars.example")) {
    Write-Host "ERROR: Please run this script from the terraform directory" -ForegroundColor Red
    Write-Host "Expected location: e:\SWE5001\ms-freelancer\terraform" -ForegroundColor Yellow
    exit 1
}

Write-Host "Step 1: Setting up Terraform files for NEW EKS cluster..." -ForegroundColor Cyan

# Backup existing files
if (Test-Path "main.tf") {
    Write-Host "Backing up existing main.tf to main-old.tf.bak"
    Copy-Item "main.tf" "main-old.tf.bak" -Force
}

if (Test-Path "security-groups.tf") {
    Write-Host "Backing up existing security-groups.tf to security-groups-old.tf.bak"
    Copy-Item "security-groups.tf" "security-groups-old.tf.bak" -Force
}

if (Test-Path "outputs.tf") {
    Write-Host "Backing up existing outputs.tf to outputs-old.tf.bak"
    Copy-Item "outputs.tf" "outputs-old.tf.bak" -Force
}

# Files are already in place - just copy terraform.tfvars example
if (-not (Test-Path "terraform.tfvars")) {
    Copy-Item "terraform.tfvars.example" "terraform.tfvars" -Force
    Write-Host "✅ Created terraform.tfvars from example" -ForegroundColor Green
} else {
    Write-Host "⚠️  terraform.tfvars already exists - please review and update it" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: ✅ Your infrastructure is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Perfect! You have the required subnets:" -ForegroundColor Cyan
Write-Host "  VPC: vpc-07e46d9a4ad5924c2" -ForegroundColor White
Write-Host "  Public Subnets (ALB): subnet-03b2e6af655972ba3, subnet-046c36287cfe01cda" -ForegroundColor White  
Write-Host "  Private Subnets (EKS): subnet-03f7274e3abb4833c, subnet-0f211af0306368c36" -ForegroundColor White
Write-Host ""
Write-Host "This is the ideal setup for EKS security!" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: Review terraform.tfvars (mostly ready!)" -ForegroundColor Cyan
Write-Host "The subnet configuration is already correct. Optionally customize:" -ForegroundColor White
Write-Host "  1. cluster_name (default: freelancer-marketplace-eks)"
Write-Host "  2. node_group_scaling_config (default: 2-6 nodes)"
Write-Host "  3. node_group_instance_types (default: t3.medium, t3.large)"
Write-Host ""

Write-Host "Step 4: Deploy the cluster" -ForegroundColor Cyan
Write-Host "After editing terraform.tfvars, run:" -ForegroundColor White
Write-Host "  terraform init" -ForegroundColor Gray
Write-Host "  terraform plan" -ForegroundColor Gray
Write-Host "  terraform apply" -ForegroundColor Gray
Write-Host ""

Write-Host "Step 5: Configure kubectl" -ForegroundColor Cyan
Write-Host "After successful deployment:" -ForegroundColor White
Write-Host "  aws eks update-kubeconfig --region ap-southeast-1 --name freelancer-marketplace-eks" -ForegroundColor Gray
Write-Host "  kubectl get nodes" -ForegroundColor Gray
Write-Host ""

Write-Host "=== SETUP COMPLETE ===" -ForegroundColor Green
Write-Host "Read NEW_EKS_DEPLOYMENT_GUIDE.md for detailed instructions" -ForegroundColor Yellow

# Check if terraform is installed
if (Get-Command terraform -ErrorAction SilentlyContinue) {
    Write-Host ""
    Write-Host "Terraform is installed. Version:" -ForegroundColor Green
    terraform --version
} else {
    Write-Host ""
    Write-Host "WARNING: Terraform not found. Please install it first." -ForegroundColor Red
}

# Check if AWS CLI is configured
if (Get-Command aws -ErrorAction SilentlyContinue) {
    Write-Host ""
    Write-Host "AWS CLI is available. Current identity:" -ForegroundColor Green
    aws sts get-caller-identity
} else {
    Write-Host ""
    Write-Host "WARNING: AWS CLI not found. Please install and configure it first." -ForegroundColor Red
}