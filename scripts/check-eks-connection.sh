#!/bin/bash

# Script to check EKS cluster connection and GitHub Actions role configuration
# Run this to diagnose the authentication issue

set -e

CLUSTER_NAME="freelancer-marketplace-eks"
AWS_REGION="ap-southeast-1"
ACCOUNT_ID="539827877726"
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/github-actions-role"

echo "=================================================="
echo "EKS Cluster Connection Check"
echo "=================================================="
echo ""

# 1. Check AWS CLI is installed
echo "1. Checking AWS CLI..."
if ! command -v aws &> /dev/null; then
    echo "✗ AWS CLI not found!"
    exit 1
fi
echo "✓ AWS CLI installed"

# 2. Check current AWS identity
echo ""
echo "2. Checking AWS credentials..."
IDENTITY=$(aws sts get-caller-identity 2>&1)
if [ $? -eq 0 ]; then
    echo "✓ AWS credentials are valid"
    echo "$IDENTITY" | jq '.'
else
    echo "✗ AWS credentials error!"
    echo "$IDENTITY"
    exit 1
fi

# 3. Check kubectl is installed
echo ""
echo "3. Checking kubectl..."
if ! command -v kubectl &> /dev/null; then
    echo "✗ kubectl not found!"
    exit 1
fi
echo "✓ kubectl installed: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"

# 4. Update kubeconfig
echo ""
echo "4. Updating kubeconfig for cluster..."
if aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME 2>&1; then
    echo "✓ Kubeconfig updated successfully"
else
    echo "✗ Failed to update kubeconfig"
    exit 1
fi

# 5. Test cluster connection
echo ""
echo "5. Testing cluster connection..."
if kubectl cluster-info &> /dev/null; then
    echo "✓ Successfully connected to cluster!"
    kubectl cluster-info
else
    echo "✗ Cannot connect to cluster"
    kubectl cluster-info
fi

# 6. Test authentication
echo ""
echo "6. Testing kubectl authentication..."
if kubectl auth can-i get pods -n default &> /dev/null; then
    echo "✓ kubectl authentication successful"
else
    echo "✗ kubectl authentication failed"
    echo "  Error: You don't have access to the cluster"
fi

# 7. Check aws-auth ConfigMap
echo ""
echo "7. Checking aws-auth ConfigMap..."
if kubectl get configmap aws-auth -n kube-system &> /dev/null; then
    echo "✓ aws-auth ConfigMap exists"
    
    echo ""
    echo "Checking if GitHub Actions role is configured..."
    if kubectl get configmap aws-auth -n kube-system -o yaml | grep -q "$ROLE_ARN"; then
        echo "✓ GitHub Actions role is already in aws-auth ConfigMap"
    else
        echo "✗ GitHub Actions role NOT FOUND in aws-auth ConfigMap"
        echo ""
        echo "This is your issue! Run this command to fix it:"
        echo ""
        echo "eksctl create iamidentitymapping \\"
        echo "  --cluster $CLUSTER_NAME \\"
        echo "  --region $AWS_REGION \\"
        echo "  --arn $ROLE_ARN \\"
        echo "  --username github-actions \\"
        echo "  --group system:masters"
    fi
    
    echo ""
    echo "Current aws-auth ConfigMap content:"
    kubectl get configmap aws-auth -n kube-system -o yaml
else
    echo "✗ Cannot access aws-auth ConfigMap"
fi

# 8. Check deployments
echo ""
echo "8. Checking existing deployments..."
if kubectl get deployments -n default &> /dev/null; then
    echo "✓ Can list deployments"
    kubectl get deployments -n default
else
    echo "✗ Cannot list deployments"
fi

echo ""
echo "=================================================="
echo "Summary"
echo "=================================================="
echo ""
echo "If you see errors above, particularly with kubectl commands,"
echo "you need to add the GitHub Actions role to the cluster's aws-auth ConfigMap."
echo ""
echo "Run: cd scripts && ./fix-eks-access.sh"
echo ""
