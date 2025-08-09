#!/bin/bash

# Main shell configuration file for the cloud Cloud DevContainer
# This file is sourced by /etc/bash.bashrc to apply these settings to all interactive shells

# Load all bash specific customization scripts from the bash directory
# These include aliases, prompt customization, environment variables, etc.
for file in /etc/devcontainer/shell/bash/*.sh; do
  [ -f "$file" ] && source "$file"
done

# Load all function scripts that provide tool-specific utilities
# These include helper functions for AWS, Docker, Terraform, GitHub, etc.
for file in /etc/devcontainer/functions/*.sh; do
  [ -f "$file" ] && source "$file"
done