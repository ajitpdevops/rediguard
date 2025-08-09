# AWS OpenID Connect Setup for GitHub Actions

## Step 1: Create OIDC Identity Provider in AWS

### Using AWS Console:
1. Go to IAM Console → Identity Providers
2. Click "Add Provider"
3. Select "OpenID Connect"
4. Provider URL: `https://token.actions.githubusercontent.com`
5. Audience: `sts.amazonaws.com`
6. Click "Get thumbprint" (AWS will auto-populate)
7. Click "Add provider"

### Using AWS CLI:
```bash
aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com \
    --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

## Step 2: Create IAM Role for GitHub Actions

### Trust Policy (github-actions-trust-policy.json):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::209479286315:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:ajitpdevops/rediguard:*"
                }
            }
        }
    ]
}
```

### Create the Role:
```bash
# Replace YOUR_ACCOUNT_ID with your actual AWS account ID
aws iam create-role \
    --role-name GitHubActionsRole \
    --assume-role-policy-document file://github-actions-trust-policy.json \
    --description "Role for GitHub Actions OIDC"

# Attach AdministratorAccess policy (or create custom policy for better security)
aws iam attach-role-policy \
    --role-name GitHubActionsRole \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

## Step 3: Get Your AWS Account ID
```bash
aws sts get-caller-identity --query Account --output text
```

## Step 4: Configure GitHub Repository Secrets

Add these secrets to your GitHub repository:
- Go to GitHub → Your Repo → Settings → Secrets and Variables → Actions
- Add the following secrets:

### Required Secrets:
- `AWS_ACCOUNT_ID`: Your AWS account ID
- `AWS_REGION`: Your preferred AWS region (e.g., us-east-1)

### Optional Secrets (for enhanced security):
- `ECR_REGISTRY`: YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com
- `ECS_CLUSTER_NAME`: rediguard-cluster
- `ECS_SERVICE_NAME`: rediguard-app

## Important Security Notes:

1. **Replace YOUR_ACCOUNT_ID** with your actual AWS account ID in all configurations
2. The trust policy restricts access to only your specific repository
3. Consider using more restrictive permissions than AdministratorAccess for production
4. The role can only be assumed from GitHub Actions in your repository

## Example Role ARN:
Your role ARN will be: `arn:aws:iam::YOUR_ACCOUNT_ID:role/GitHubActionsRole`
