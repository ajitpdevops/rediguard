#------------------------------------------------------------------------------#
# DOCKER HELPER FUNCTIONS                                                      #
#------------------------------------------------------------------------------#

# Start docker service.
cloudDockerStart() {
  echo "🟢 Starting Docker"
  sudo service docker start > /dev/null 2>&1
  # Give Docker a few seconds to initialize
  sleep 2
  # Check if Docker is actually responding
  if ! docker info > /dev/null 2>&1; then
      echo "🔴 Docker did not start successfully."
      echo "🔴 This can happen if another DevContainer instance is already running Docker."
      echo "🔴 Please shut down any other DevContainer using Docker, then try again."
      echo "🔴 Press Enter to continue anyway..."
      read
  else
      echo "🟢 Docker started!"
  fi
}

# Stop docker service.
cloudDockerStop() {
  echo "🟢 Stopping Docker"
  sudo service docker stop
  echo "🟢 Docker stopped!"
}

# Authenticate Docker to GitHub Container Registry (GHCR).
cloudDockerLoginGHCR() {

  # export github required env vars.
  cloudGitHubExport

  # remove any existing credstore.
  _cloud_docker_remove_credstore

  echo "🟢 Authenticating Docker with GHCR"

  # docker login using gh user and token. 
  echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USER" --password-stdin \
    || { echo "🔴 Docker login to ghcr.io failed"; return 1; }

  echo "🟢 Docker authenticated with GHCR as $GITHUB_USER"
}

# Authenticate Docker to AWS Elastic Container Registry (ECR)
cloudDockerLoginECR() {

  echo "🟢 Authenticating Docker with ECR"

  # ensure aws profile vars are set.
  if [ -z "$AWS_PROFILE" ]; then
    echo "🔴 AWS_PROFILE missing; run cloudAWSLogin or cloudAWSProfile"
    return 1
  fi

  # export all required aws env vars. 
  cloudAWSExport

  # remove any existing credstore.
  _cloud_docker_remove_credstore

  # docker login ecr. 
  echo "$(aws ecr get-login-password --region "$AWS_REGION")" \
    | docker login \
        --username AWS \
        --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com" \
    || { echo "🔴 Docker login to ECR failed"; return 1; }

  echo "🟢 Docker authenticated with ECR ($AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com)"
}


#------------------------------------------------------------------------------#
# SHARED HELPER FUNCTIONS                                                      #
#------------------------------------------------------------------------------#

# Remove credsstore as a workaround to vscode issues. 
_cloud_docker_remove_credstore() {
  local config_file="$HOME/.docker/config.json"

  # check for config file.
  if [[ ! -f "$config_file" ]]; then
    return 0
  fi

  # if credstore exists remove it. 
  if grep -q '"credsStore"' "$config_file"; then
    echo ""
    echo "🟢 Removing CredsStore from $config_file..."
    sed -i '/"credsStore"[[:space:]]*:/d' "$HOME/.docker/config.json"
    echo "🟢 CredsStore removed."
    echo ""
  else
   return 0
  fi
}