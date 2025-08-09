#!/bin/bash

# Validate GitHub Secrets Configuration
# This script helps verify that all required secrets are properly configured

echo "🔍 GitHub Secrets Validation Checklist"
echo "======================================"
echo ""

# Required secrets
REQUIRED_SECRETS=(
    "AWS_ACCOUNT_ID"
    "AWS_REGION" 
    "ECR_REGISTRY"
    "ECS_CLUSTER_NAME"
    "ECS_SERVICE_NAME"
)

echo "📋 Required GitHub Repository Secrets:"
echo ""

for secret in "${REQUIRED_SECRETS[@]}"; do
    echo "□ $secret"
done

echo ""
echo "🔧 How to configure GitHub Secrets:"
echo "1. Go to your GitHub repository"
echo "2. Navigate to Settings → Secrets and Variables → Actions"
echo "3. Click 'New repository secret'"
echo "4. Add each secret with the appropriate value"
echo ""

# Check if AWS CLI is available and configured
echo "🔍 Local AWS Configuration Check:"
echo "================================"

if command -v aws &> /dev/null; then
    echo "✅ AWS CLI is installed"
    
    if aws sts get-caller-identity &> /dev/null; then
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
        AWS_REGION=$(aws configure get region 2>/dev/null || echo "not-set")
        
        echo "✅ AWS CLI is configured"
        echo "   Account ID: $AWS_ACCOUNT_ID"
        echo "   Region: $AWS_REGION"
        echo ""
        
        echo "📝 Suggested Secret Values:"
        echo "=========================="
        echo "AWS_ACCOUNT_ID: $AWS_ACCOUNT_ID"
        echo "AWS_REGION: $AWS_REGION"
        echo "ECR_REGISTRY: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
        echo "ECS_CLUSTER_NAME: rediguard-cluster"
        echo "ECS_SERVICE_NAME: rediguard-app"
        echo ""
        
    else
        echo "❌ AWS CLI not configured. Run 'aws configure' first."
    fi
else
    echo "❌ AWS CLI not installed"
fi

# Check if ECR repositories exist
echo "🐳 ECR Repository Check:"
echo "======================="

if command -v aws &> /dev/null && aws sts get-caller-identity &> /dev/null; then
    AWS_REGION=$(aws configure get region 2>/dev/null || echo "us-east-1")
    
    for repo in "rediguard-backend" "rediguard-frontend"; do
        if aws ecr describe-repositories --repository-names "$repo" --region "$AWS_REGION" &> /dev/null; then
            echo "✅ $repo repository exists"
        else
            echo "❌ $repo repository not found"
            echo "   Run: aws ecr create-repository --repository-name $repo --region $AWS_REGION"
        fi
    done
else
    echo "⚠️  Cannot check ECR repositories (AWS CLI not configured)"
fi

echo ""
echo "🔐 OIDC Role Check:"
echo "=================="

if command -v aws &> /dev/null && aws sts get-caller-identity &> /dev/null; then
    if aws iam get-role --role-name GitHubActionsRole &> /dev/null; then
        echo "✅ GitHubActionsRole exists"
        
        # Check if OIDC provider exists
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
        if aws iam list-open-id-connect-providers | grep "token.actions.githubusercontent.com" &> /dev/null; then
            echo "✅ GitHub OIDC provider exists"
        else
            echo "❌ GitHub OIDC provider not found"
            echo "   See docs/AWS_OIDC_SETUP.md for setup instructions"
        fi
    else
        echo "❌ GitHubActionsRole not found"
        echo "   See docs/AWS_OIDC_SETUP.md for setup instructions"
    fi
else
    echo "⚠️  Cannot check OIDC role (AWS CLI not configured)"
fi

echo ""
echo "🧪 Quick Test Commands:"
echo "======================"
echo "# Test ECR login:"
echo "aws ecr get-login-password --region \$AWS_REGION | docker login --username AWS --password-stdin \$ECR_REGISTRY"
echo ""
echo "# Test role assumption (from GitHub Actions):"
echo "aws sts assume-role-with-web-identity --role-arn arn:aws:iam::\$AWS_ACCOUNT_ID:role/GitHubActionsRole --role-session-name test --web-identity-token \$GITHUB_TOKEN"
echo ""
echo "# Test ECR repository access:"
echo "aws ecr describe-repositories --repository-names rediguard-backend rediguard-frontend"
echo ""

echo "📚 Documentation:"
echo "================"
echo "• CI/CD Setup: docs/CICD_SETUP.md"
echo "• OIDC Setup: docs/AWS_OIDC_SETUP.md"
echo "• ECR Setup: scripts/setup-ecr.sh"
echo ""

echo "✅ Validation complete!"
echo ""
echo "Next steps:"
echo "1. Configure all required GitHub secrets"
echo "2. Ensure ECR repositories exist"
echo "3. Verify OIDC role and provider are set up"
echo "4. Test by pushing to a feature branch"
echo "5. Merge to main to trigger deployment"
