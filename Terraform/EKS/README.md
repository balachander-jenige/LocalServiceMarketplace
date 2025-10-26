# EKS Cluster Deployment# 🚀 Terraform Infrastructure Deployment Guide

This Terraform configuration creates a **new EKS cluster** in your existing VPC with the following architecture:## 📋 Overview

````This Terraform configuration creates the complete infrastructure needed for your freelancer marketplace, matching your existing EKS cluster setup. It handles the traffic flow: **Internet → ALB (Public Subnet) → EKS Pods (Private Subnet) → Managed Databases**.

Internet → ALB (Public Subnets) → EKS Cluster (Private Subnets) → Your Applications

```## 🏗️ Infrastructure Components Created



## Quick Start### **🌐 Network & Security**



1. **Copy configuration:**- **7 Security Groups** - Complete traffic flow control

   ```powershell- **ALB Integration** - Internet-facing load balancer in public subnets

   Copy-Item terraform.tfvars.example terraform.tfvars- **EKS Integration** - Secure communication to pods in private subnets

````

### **🗄️ Database Integration**

2. **Deploy:**

   ````powershell- **Uses Existing Managed Databases** - Your existing RDS/DocumentDB endpoints

   terraform init- **No Database Creation** - Terraform focuses on networking and security only

   terraform plan- **K8s Secrets Integration** - Your existing database connection strings in K8s

   terraform apply

   ```### **🔐 SSL/TLS**

   ````

3. **Configure kubectl:**- **ACM Certificate** - For custom domain HTTPS

   ```powershell- **S3 Bucket** - ALB access logs storage

   aws eks update-kubeconfig --region ap-southeast-1 --name freelancer-marketplace-eks

   kubectl get nodes### **🔑 IAM & Access**

   ```

- **IAM Roles** - EKS access to Secrets Manager

## What's Included- **Database Monitoring** - Enhanced monitoring roles

- ✅ **EKS Cluster** with managed node group## 📝 Required Input Variables

- ✅ **Security Groups** for ALB ↔ EKS communication

- ✅ **IAM Roles** (uses your existing roles or creates new ones)You need to provide these values in `terraform.tfvars`:

- ✅ **S3 Bucket** for ALB access logs

- ✅ **OIDC Provider** for service accounts```bash

# 🔴 REQUIRED - Your existing network infrastructure

## Your Infrastructurevpc_id = "vpc-07e46d9a4ad5924c2" # Your VPC ID

- **VPC**: `vpc-07e46d9a4ad5924c2`public_subnet_ids = [

- **Public Subnets** (ALB): `subnet-03b2e6af655972ba3`, `subnet-046c36287cfe01cda` "subnet-03f7274e3abb4833c", # Public subnet for ALB

- **Private Subnets** (EKS): `subnet-03f7274e3abb4833c`, `subnet-0f211af0306368c36` "subnet-0f211af0306368c36" # Second AZ for HA

- **IAM Roles**: Will use your existing cluster/node roles]

## Filesprivate_subnet_ids = [

"subnet-xxxxxxxxxxxxxxxx", # Private subnet with EKS nodes

- `main.tf` - EKS cluster and infrastructure "subnet-xxxxxxxxxxxxxxxx" # Second AZ for HA

- `security-groups.tf` - Network security rules]

- `outputs.tf` - Useful outputs for integration

- `variables.tf` - Configuration variables# 🔴 REQUIRED - Unique S3 bucket name

- `terraform.tfvars.example` - Example configuration (pre-filled with your values)access_logs_bucket = "freelancer-alb-logs-your-account-123"

- `setup.ps1` - PowerShell helper script

- `NEW_EKS_DEPLOYMENT_GUIDE.md` - Detailed deployment guide# ⚠️ SECURITY - Restrict for production

office_ip_cidr = "YOUR.OFFICE.IP.RANGE/24"

## Next Steps```

After deployment, install the AWS Load Balancer Controller and deploy your applications. See `NEW_EKS_DEPLOYMENT_GUIDE.md` for complete instructions.## 🚀 Deployment Steps

### **Step 1: Prepare Terraform**

```bash
# Navigate to terraform directory
cd terraform

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your actual values

# Initialize Terraform
terraform init
```

### **Step 2: Plan and Validate**

```bash
# Check what will be created
terraform plan

# Validate configuration
terraform validate
```

### **Step 3: Deploy Infrastructure**

```bash
# Apply the configuration
terraform apply

# Review the plan and type 'yes' to confirm
```

### **Step 4: Get Security Group IDs**

```bash
# Get all security group IDs for K8s ingress configuration
terraform output security_group_ids

# Get ALB security group ID specifically
terraform output alb_security_group_id

# Get EKS nodes security group ID
terraform output eks_nodes_security_group_id
```

## 🔗 Network Traffic Flow

This infrastructure creates the exact traffic flow you requested:

```
Internet (HTTPS/HTTP)
       ↓
Application Load Balancer (Public Subnets)
       ↓ [ALB Security Group → EKS Nodes Security Group]
EKS Worker Nodes (Private Subnets)
       ↓ [Gateway Service → Microservices]
Internal Pod Communication
       ↓ [EKS Nodes Security Group → Database Security Groups]
Managed Databases (RDS/DocumentDB)
```

### **Security Group Rules Created:**

1. **ALB Security Group**

   - **Inbound**: HTTP (80), HTTPS (443) from internet
   - **Outbound**: All traffic to EKS nodes

2. **EKS Nodes Security Group**

   - **Inbound**: Gateway port (8081) from ALB
   - **Inbound**: Internal communication between pods
   - **Outbound**: All traffic (databases, internet)

3. **Existing Database Security** (managed externally)
   - Your existing databases should allow access from EKS security group
   - Configure your existing database security groups to allow EKS nodes

## 🔧 Integration with Existing K8s

### **Update Your Ingress**

Use the security group ID in your ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    alb.ingress.kubernetes.io/security-groups: "sg-xxxxxxxxx" # From terraform output
```

### **Use Existing Database Secrets**

```bash
# Your K8s secrets should already contain database connection strings
# Example (update with your actual endpoints):
kubectl create secret generic auth-secrets \
  --from-literal=database-url="postgresql://user:pass@your-rds-endpoint:5432/dbname" \
  --from-literal=jwt-secret-key="your-jwt-secret"

kubectl create secret generic notification-secrets \
  --from-literal=mongodb-url="mongodb://user:pass@your-docdb-endpoint:27017/dbname?ssl=true"
```

### **Deploy Your Services**

```bash
# Deploy infrastructure (Redis, RabbitMQ only)
kubectl apply -f infrastructure/redis-k8s.yaml
kubectl apply -f infrastructure/rabbitmq-k8s.yaml

# Deploy microservices
kubectl apply -f services/*/k8s-deployment.yaml
kubectl apply -f gateway-service/k8s-deployment.yaml

# Deploy ingress (will use your security groups)
kubectl apply -f k8s/ingress-no-domain.yaml
```

## 📊 Outputs Provided

After deployment, you'll get:

```bash
# Security Groups
alb_security_group_id           = "sg-xxxxxxxxx"
eks_nodes_security_group_id     = "sg-xxxxxxxxx"

# Existing Database References (if provided)
existing_rds_endpoint           = "your-rds-endpoint"
existing_documentdb_endpoint    = "your-docdb-endpoint"

# Certificate (if created)
acm_certificate_arn            = "arn:aws:acm:..."

# Ingress Configuration
ingress_annotations            = {...}
```

## 🔍 Testing the Setup

### **Verify Security Groups**

```bash
# Check ALB can reach EKS nodes
aws ec2 describe-security-groups --group-ids $(terraform output -raw alb_security_group_id)

# Check EKS nodes can reach databases
aws ec2 describe-security-groups --group-ids $(terraform output -raw eks_nodes_security_group_id)
```

### **Test Database Connectivity**

```bash
# Test RDS connection from EKS
kubectl run test-pod --image=postgres:15 --rm -it -- psql "$(terraform output -raw rds_connection_string)"

# Test DocumentDB connection
kubectl run test-pod --image=mongo:4.4 --rm -it -- mongo "$(terraform output -raw documentdb_connection_string)"
```

### **Verify ALB Integration**

```bash
# Get ALB DNS name
kubectl get ingress

# Test HTTP/HTTPS endpoints
curl -I https://your-alb-dns/api/v1/health
```

## 🎯 Production Checklist

Before using in production:

- [ ] Set `enable_deletion_protection = true`
- [ ] Restrict `allowed_cidr_blocks` to specific IP ranges
- [ ] Set up proper `office_ip_cidr` for management access
- [ ] Configure Terraform backend for state storage
- [ ] Enable CloudTrail and GuardDuty
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategies for databases

## 🔧 Customization Options

### **Database Sizing**

```hcl
# For production workloads
rds_instance_class = "db.t3.large"
documentdb_instance_class = "db.r5.large"
```

### **High Availability**

```hcl
# Enable Multi-AZ for RDS
multi_az = true

# Add more DocumentDB instances
documentdb_instance_count = 2
```

### **Custom Domain**

```hcl
create_certificate = true
domain_name = "api.yourdomain.com"
```

This Terraform configuration provides a production-ready infrastructure that perfectly matches your existing EKS setup and supports the traffic flow you described! 🎉
