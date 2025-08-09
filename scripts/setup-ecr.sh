#!/bin/bash

# ECR Repository Setup Script for Rediguard
# This script creates the necessary ECR repositories for the CI/CD pipeline

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
BACKEND_REPO="rediguard-backend"
FRONTEND_REPO="rediguard-frontend"

echo "🚀 Setting up ECR repositories for Rediguard..."
echo "AWS Region: $AWS_REGION"

# Function to create ECR repository
create_ecr_repo() {
    local repo_name=$1
    echo "Creating ECR repository: $repo_name"
    
    if aws ecr describe-repositories --repository-names "$repo_name" --region "$AWS_REGION" >/dev/null 2>&1; then
        echo "✅ Repository $repo_name already exists"
    else
        aws ecr create-repository \
            --repository-name "$repo_name" \
            --region "$AWS_REGION" \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256
        
        echo "✅ Created repository: $repo_name"
    fi
    
    # Set lifecycle policy to manage image retention
    echo "Setting lifecycle policy for $repo_name..."
    aws ecr put-lifecycle-policy \
        --repository-name "$repo_name" \
        --region "$AWS_REGION" \
        --lifecycle-policy-text '{
            "rules": [
                {
                    "rulePriority": 1,
                    "description": "Keep last 10 images",
                    "selection": {
                        "tagStatus": "tagged",
                        "countType": "imageCountMoreThan",
                        "countNumber": 10
                    },
                    "action": {
                        "type": "expire"
                    }
                },
                {
                    "rulePriority": 2,
                    "description": "Delete untagged images older than 1 day",
                    "selection": {
                        "tagStatus": "untagged",
                        "countType": "sinceImagePushed",
                        "countUnit": "days",
                        "countNumber": 1
                    },
                    "action": {
                        "type": "expire"
                    }
                }
            ]
        }'
    
    echo "✅ Lifecycle policy set for $repo_name"
}

# Check AWS CLI is configured
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS CLI not configured or no access. Please run 'aws configure' first."
    exit 1
fi

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $AWS_ACCOUNT_ID"

# Create repositories
create_ecr_repo "$BACKEND_REPO"
create_ecr_repo "$FRONTEND_REPO"

# Display repository information
echo ""
echo "📋 ECR Repository Summary:"
echo "========================="

for repo in "$BACKEND_REPO" "$FRONTEND_REPO"; do
    repo_uri=$(aws ecr describe-repositories --repository-names "$repo" --region "$AWS_REGION" --query 'repositories[0].repositoryUri' --output text)
    echo "Repository: $repo"
    echo "URI: $repo_uri"
    echo ""
done

# Display GitHub Secrets
echo "🔧 GitHub Repository Secrets:"
echo "============================="
echo "Make sure these secrets are configured in your GitHub repository:"
echo ""
echo "AWS_ACCOUNT_ID: $AWS_ACCOUNT_ID"
echo "AWS_REGION: $AWS_REGION"
echo "ECR_REGISTRY: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
echo "ECS_CLUSTER_NAME: rediguard-cluster (if using ECS)"
echo "ECS_SERVICE_NAME: rediguard-app (if using ECS)"
echo ""

# Test ECR login
echo "🧪 Testing ECR login..."
if aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"; then
    echo "✅ ECR login successful"
else
    echo "❌ ECR login failed"
    exit 1
fi

echo ""
echo "🎉 ECR setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Commit and push your code to trigger the CI/CD pipeline"
echo "2. Check GitHub Actions for build and deployment status"
echo "3. Monitor ECR repositories for pushed images"
