#!/bin/bash

# AWS OIDC Setup Script for GitHub Actions
# This script sets up OpenID Connect between GitHub Actions and AWS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
GITHUB_REPO="ajitpdevops/rediguard"
ROLE_NAME="GitHubActionsRole"
POLICY_NAME="RediguardDeploymentPolicy"

echo -e "${GREEN}🔧 Setting up AWS OIDC for GitHub Actions${NC}"
echo "Repository: $GITHUB_REPO"
echo "Role Name: $ROLE_NAME"
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✅ AWS Account ID: $AWS_ACCOUNT_ID${NC}"

# Check if OIDC provider already exists
echo -e "${YELLOW}🔍 Checking for existing OIDC provider...${NC}"
if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "arn:aws:iam::$AWS_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com" &> /dev/null; then
    echo -e "${GREEN}✅ OIDC provider already exists${NC}"
else
    echo -e "${YELLOW}📝 Creating OIDC provider...${NC}"
    aws iam create-open-id-connect-provider \
        --url https://token.actions.githubusercontent.com \
        --client-id-list sts.amazonaws.com \
        --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
    echo -e "${GREEN}✅ OIDC provider created${NC}"
fi

# Update trust policy with actual account ID
echo -e "${YELLOW}📝 Updating trust policy...${NC}"
sed "s/YOUR_ACCOUNT_ID/$AWS_ACCOUNT_ID/g" docs/github-actions-trust-policy.json > /tmp/trust-policy.json

# Create IAM role
echo -e "${YELLOW}📝 Creating IAM role...${NC}"
if aws iam get-role --role-name $ROLE_NAME &> /dev/null; then
    echo -e "${YELLOW}⚠️  Role $ROLE_NAME already exists, updating trust policy...${NC}"
    aws iam update-assume-role-policy \
        --role-name $ROLE_NAME \
        --policy-document file:///tmp/trust-policy.json
else
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file:///tmp/trust-policy.json \
        --description "Role for GitHub Actions OIDC - Rediguard deployment"
    echo -e "${GREEN}✅ IAM role created${NC}"
fi

# Create custom policy for deployment
echo -e "${YELLOW}📝 Creating custom deployment policy...${NC}"
if aws iam get-policy --policy-arn "arn:aws:iam::$AWS_ACCOUNT_ID:policy/$POLICY_NAME" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Policy $POLICY_NAME already exists${NC}"
else
    aws iam create-policy \
        --policy-name $POLICY_NAME \
        --policy-document file://docs/rediguard-deployment-policy.json \
        --description "Custom policy for Rediguard deployment via GitHub Actions"
    echo -e "${GREEN}✅ Custom policy created${NC}"
fi

# Attach policies to role
echo -e "${YELLOW}📝 Attaching policies to role...${NC}"

# For development/testing - use AdministratorAccess (comment out for production)
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# For production - use custom policy (uncomment for production)
# aws iam attach-role-policy \
#     --role-name $ROLE_NAME \
#     --policy-arn "arn:aws:iam::$AWS_ACCOUNT_ID:policy/$POLICY_NAME"

echo -e "${GREEN}✅ Policies attached${NC}"

# Display results
echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo -e "${YELLOW}📋 GitHub Repository Secrets to Add:${NC}"
echo "AWS_ACCOUNT_ID: $AWS_ACCOUNT_ID"
echo "AWS_REGION: us-east-1  # or your preferred region"
echo "AWS_ROLE_ARN: arn:aws:iam::$AWS_ACCOUNT_ID:role/$ROLE_NAME"
echo ""
echo -e "${YELLOW}🔗 Add these secrets at:${NC}"
echo "https://github.com/$GITHUB_REPO/settings/secrets/actions"
echo ""
echo -e "${GREEN}✅ Your GitHub Actions can now authenticate with AWS using OIDC!${NC}"

# Clean up
rm -f /tmp/trust-policy.json
