#!/bin/bash

# AWS CLI completion
if command -v aws_completer >/dev/null 2>&1; then
  complete -C "$(command -v aws_completer)" aws
fi

# AWS profile completion
_awsprofile_completer() {
  local cur profiles
  cur="${COMP_WORDS[COMP_CWORD]}"
  profiles=$(grep '^\[profile' ~/.aws/config | sed -E 's/^\[profile (.*)\]/\1/')
  COMPREPLY=($(compgen -W "${profiles}" -- "$cur"))
}
complete -F _awsprofile_completer cloudAWSLogin
complete -F _awsprofile_completer cloudAWSProfile

# GitHub CLI completion
if command -v gh >/dev/null 2>&1; then
  if [[ -n "$ZSH_VERSION" ]]; then
    eval "$(gh completion -s zsh)"
  else
    eval "$(gh completion -s bash)"
  fi
fi

#------------------------------------------------------------------------------#
# CUSTOM cloud FUNCTION COMPLETIONS                                           #
#------------------------------------------------------------------------------#

# Repository completion for cloudRepos and cloudReposCode
_repos_completer() {
  local cur repos_dir
  cur="${COMP_WORDS[COMP_CWORD]}"
  repos_dir="/workspaces/repos"

  if [[ -d "$repos_dir" ]]; then
    local repos=$(find "$repos_dir" -maxdepth 1 -type d -exec basename {} \; | grep -v "^repos$")
    COMPREPLY=($(compgen -W "${repos}" -- "$cur"))
  fi
}
complete -F _repos_completer cloudRepos
complete -F _repos_completer cloudReposCode

# GitHub organization completion for cloudGitHubFixRemote
_github_org_completer() {
  local cur orgs
  cur="${COMP_WORDS[COMP_CWORD]}"
  # Common GitHub organizations - can be customized
  orgs="cloudorg microsoft google facebook netflix kubernetes"
  COMPREPLY=($(compgen -W "${orgs}" -- "$cur"))
}
complete -F _github_org_completer cloudGitHubFixRemote
complete -F _github_org_completer cloudGitHubFixAllRemotes

# Terraform workspace completion
if command -v terraform >/dev/null 2>&1; then
  _terraform_workspace_completer() {
    local cur workspaces
    cur="${COMP_WORDS[COMP_CWORD]}"
    workspaces=$(terraform workspace list 2>/dev/null | grep -v "^\*" | sed 's/^[[:space:]]*//')
    COMPREPLY=($(compgen -W "${workspaces}" -- "$cur"))
  }
  complete -F _terraform_workspace_completer terraform
fi

# Docker container completion for common commands
if command -v docker >/dev/null 2>&1; then
  _docker_container_completer() {
    local cur containers
    cur="${COMP_WORDS[COMP_CWORD]}"
    containers=$(docker ps --format "table {{.Names}}" | tail -n +2)
    COMPREPLY=($(compgen -W "${containers}" -- "$cur"))
  }
  complete -F _docker_container_completer docker exec
  complete -F _docker_container_completer docker logs
  complete -F _docker_container_completer docker stop
  complete -F _docker_container_completer docker restart
fi

# File extension completions for common tools
_file_extension_completer() {
  local cur
  cur="${COMP_WORDS[COMP_CWORD]}"

  case "${COMP_WORDS[0]}" in
    code|vim|nano)
      COMPREPLY=($(compgen -f -X '!*.@(js|ts|py|md|json|yaml|yml|sh|tf)' -- "$cur"))
      ;;
    *)
      COMPREPLY=($(compgen -f -- "$cur"))
      ;;
  esac
}
complete -F _file_extension_completer code
complete -F _file_extension_completer vim
complete -F _file_extension_completer nano

echo "🟢 Custom completions loaded!"