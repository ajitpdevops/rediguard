#------------------------------------------------------------------------------#
# AWS HELPER FUNCTIONS                                                         #
# This file contains utility functions for working with AWS in the DevContainer#
#------------------------------------------------------------------------------#

# Function: cloudAWSPopulateConfig
# Description:
#   Automates the AWS SSO configuration process by:
#   1. Logging into AWS SSO using aws-sso-util
#   2. Populating AWS config with available roles and accounts
#   3. Formatting account and role names for consistency
#
# Usage: cloudAWSPopulateConfig
cloudAWSPopulateConfig() {

  echo "🟢 Starting AWS config population"

  # Authenticate to AWS SSO
  aws-sso-util login || {
    echo "🔴 SSO login failed"
    return 1
  }

  # Generate AWS config profiles from available SSO accounts and roles
  # Options:
  #   --account-name-case lower: Convert account names to lowercase
  #   --role-name-case lower: Convert role names to lowercase
  #   --trim-role-name: Remove 'cloud' prefix from role names
  #   --trim-account-name: Remove 'cloud-avm-' prefix from account names
  #   --existing-config-action overwrite: Replace existing config
  aws-sso-util configure populate \
    --account-name-case lower \
    --role-name-case lower \
    --trim-role-name '^cloud' \
    --trim-account-name '^cloud-avm-' \
    --existing-config-action overwrite || {
      echo "🔴 Failed to populate AWS config"
      return 1
    }
  echo "🟢 AWS config populated"
}

# Function: To list available AWS SSO profiles.
# Usage: cloudAWSListProfiles
cloudAWSListProfiles() {
  echo "🟢 Listing available AWS SSO profiles"

  # List profiles using aws-sso-util
  aws-sso-util roles || {
    echo "🔴 Failed to list AWS SSO profiles; did you run 'cloudAWSPopulateConfig?"
    return 1
  }

  echo "🟢 Completed listing AWS SSO profiles"
}

# Export AWS environment variables for a profile.
cloudAWSProfile() {

  # validate usage.
  profile=$1
  if [ -z "$profile" ]; then
    echo "🟡 Usage: cloudAWSProfile <profile>"
    return 1
  fi

  echo "🟢 Setting profile to: $profile"

  # export active aws profile.
  export AWS_PROFILE=$profile

  # export aws session required vars.
  cloudAWSExport "$profile" || return 1

  echo "🟢 Completed profile update"
}

# Log in via AWS SSO and then export profile.
cloudAWSLogin() {

  # validate usage.
  profile=$1
  if [ -z "$profile" ]; then
    echo "🟡 Usage: cloudAWSLogin <profile>"
    return 1
  fi

  echo "🟢 Starting AWS login for: $profile"

  # login using aws sso.
  aws sso login --profile "$profile" || {
    echo "🔴 AWS SSO login failed for profile: $profile"
    return 1
  }

  # export profile.
  export AWS_PROFILE=$profile

  # export aws session required vars.
  cloudAWSExport || return 1

  # completed
  echo "🟢 Completed AWS login"
}

# Export all required aws session env vars.
cloudAWSExport() {

  local profile=$AWS_PROFILE

  # require AWS_PROFILE to be set
  if [[ -z "$profile" ]]; then
    echo "🔴 No AWS_PROFILE set. Run 'cloudAWSLogin' or 'cloudAWSProfile' first."
    return 1
  fi

  echo "🟢 Starting AWS exports"

  # verify credentials are available
  if ! creds=$(aws configure export-credentials --profile "$profile" --format env 2>/dev/null); then
    echo "🔴 Failed to export credentials; did you run 'cloudAWSLogin $profile'?"
    return 1
  fi
  eval "$creds"

  # export region
  local region
  region=$(aws configure get region --profile "$profile")
  if [[ -z "$region" ]]; then
    echo "🔴 No region set in profile '$profile'"
    return 1
  fi
  export AWS_REGION=$region
  echo "🟢 Exported AWS_REGION: $AWS_REGION"

  # export account alias
  local acct_name
  acct_name=$(aws iam list-account-aliases --profile "$profile" --output text --query 'AccountAliases[0]' 2>/dev/null)
  export AWS_ACCOUNT_NAME="${acct_name:-unknown}"
  echo "🟢 Exported AWS_ACCOUNT_NAME: $AWS_ACCOUNT_NAME"

  # export account ID
  local acct_id
  acct_id=$(aws sts get-caller-identity --profile "$profile" --output text --query 'Account' 2>/dev/null)
  if [[ -z "$acct_id" ]]; then
    echo "🔴 Could not retrieve account ID from profile: $profile"
    return 1
  fi
  export AWS_ACCOUNT_ID=$acct_id
  echo "🟢 Exported AWS_ACCOUNT_ID: $AWS_ACCOUNT_ID"

  # export role name
  local role
  role=$(aws sts get-caller-identity --profile "$profile" --query 'Arn' --output text 2>/dev/null | awk -F'/' '{print $2}')
  export AWS_ROLE="${role:-unknown}"
  echo "🟢 Exported AWS_ROLE: $AWS_ROLE"

  # export AWS_PROFILE to reflect current
  export AWS_PROFILE=$profile
  echo "🟢 Exported AWS_PROFILE: $AWS_PROFILE"

  # completed
  echo "🟢 Completed AWS exports"
}
