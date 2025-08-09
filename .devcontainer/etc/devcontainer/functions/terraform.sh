
#------------------------------------------------------------------------------#
# TERRAFORM HELPER FUNCTIONS                                                   #
# This file contains utility functions for working with Terraform projects     #
# with environment-specific configurations (dev, stage, prod)                  #
#------------------------------------------------------------------------------#

# Function: cloudTerraformInit
# Description:
#   Initializes a Terraform project with the correct backend configuration
#   for a specific environment (dev, stage, prod)
#
# Parameters:
#   $1 - Environment name (dev|stage|prod)
#
# Usage: cloudTerraformInit dev
cloudTerraformInit() {
 
  echo "🟢 Starting Terrform Init"

  # Run common environment setup function
  _cloud_terraform_setup "$1" || return 1

  # Initialize Terraform with environment-specific backend config
  # Assumes backend/<env>.config files exist with appropriate settings
  terraform init -backend-config=backend/$env.config || return 1

  echo "🟢 Terrform Init completed!"
}

# Function: cloudTerraformPlan
# Description:
#   Runs terraform plan with the correct environment configuration
#
# Parameters:
#   $1 - Environment name (dev|stage|prod)
#
# Usage: cloudTerraformPlan prod
cloudTerraformPlan() {

  echo "🟢 Starting Terrform Plan"

  # Run common environment setup function 
  _cloud_terraform_setup "$1" || return 1

  # Add common vars support if the file exists.
  TFVARS_COMMON=""
  if [[ -f "env/common.tfvars" ]]; then
    TFVARS_COMMON='--var-file=env/common.tfvars'
  fi

  # Run plan 
  terraform plan $TFVARS_COMMON --var-file="env/${env}.tfvars"

  echo "🟢 Terrform Plan completed!"
}


#------------------------------------------------------------------------------#
# SHARED HELPER FUNCTIONS                                                      #
#------------------------------------------------------------------------------#

_cloud_terraform_setup() {
  env=$1

  # Validate environment
  case "$env" in
    dev|stage|prod) ;;
    *)
      echo "🟡 Usage: $FUNCNAME <dev|stage|prod>"
      return 1
      ;;
  esac

  # Check for AWS credentials
  if [ -z "$AWS_SESSION_TOKEN" ]; then
    echo "🔴 AWS credentials missing, run cloudAWSLogin"
    return 1
  fi

  # Set GitHub token
  cloudGitHubExport || return 1

  # Ensure we're in the infra directory
  if [ -f "infra/main.tf" ]; then
    cd infra || {
      "🔴 Failed to enter 'infra' directory"
      return 1
    }
  elif [ ! -f "main.tf" ]; then
    echo "🔴 You must run this from the project root or infra directory"
    return 1
  fi

  return 0
}