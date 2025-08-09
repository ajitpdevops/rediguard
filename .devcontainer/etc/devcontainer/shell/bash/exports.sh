#!/bin/bash

#------------------------------------------------------------------------------#
# Environment Variable Exports                                                 #
# ==========================================================================   #
#                                                                              #
# This script sets up essential environment variables for the dev container.   #
# These variables are used by various scripts and tools in the environment.    #
#------------------------------------------------------------------------------#

# CONTAINER environment variables
# - CONTAINER_WORKSPACE: Sets the workspace directory path, uses current directory if not set
# - CONTAINER_UID/GID: Current user's ID and group ID for permission management
export CONTAINER_WORKSPACE="${CONTAINER_WORKSPACE:-$(pwd)}"  
export CONTAINER_UID=$(id -u)                                
export CONTAINER_GID=$(id -g)                        

# REPOSITORY environment variables
# - REPO_URL: Git repository URL from origin remote
# - REPO_NAME: Repository name extracted from the URL (without .git extension)
export REPO_URL=$(git -C "$CONTAINER_WORKSPACE" config --get remote.origin.url)  
export REPO_NAME=$(basename -s .git "$REPO_URL")


