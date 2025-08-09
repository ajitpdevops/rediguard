#------------------------------------------------------------------------------#
# GITHUB HELPERS                                                              #
#------------------------------------------------------------------------------#

# Export GH_TOKEN into the environment
cloudGitHubExport() {
  local token
  local user 

  echo "🟢 Exporting GitHub credentials"

  # fetch github token from github cli. 
  token=$(gh auth token 2>/dev/null) || {
    echo "🔴 Could not retrieve GitHub token, run cloudGitHubLogin"
    return 1
  }

  # export token.
  export GITHUB_TOKEN=$token
  echo "🟢 Exported GITHUB_TOKEN:$GITHUB_TOKEN"

  # get user login from gh cli. 
  user=$(gh api user --jq '.login') || {
    echo "🔴 Could not get GitHub user, run cloudGitHubLogin"
    return 1
  }

  # export token.
  export GITHUB_USER=$user
  echo "🟢 Exported GITHUB_USER:$GITHUB_USER"
}

# Log in to GitHub and set up git config
cloudGitHubLogin() {

  echo "🟢 Authenticating to GitHub"

  # github cli auth.
  gh auth login -h github.com -p https -w \
    -s read:packages,write:packages,delete:packages,workflow || {
      echo "🔴 GitHub auth failed"
      return 1
    }

  # export github cli env vars. 
  cloudGitHubExport

  echo "🟢 Successfully Authenticated to GitHub"
}

# Setup Git for GItHub Cli. 
cloudGitHubSetup() {

  echo "🟢 Configureing Git for GitHub"

  # setup git auth for github cli. 
  gh auth setup-git || {
    echo "🔴 GitHub setup-git command failed"
    return 1
  }

  echo "🟢 Configureing Git User: $(gh api user --jq .name)"
  [ -z "$(git config --global user.name)" ] && \
    git config --global user.name "$(gh api user --jq .name)"
  echo "🟢 Configureing Git Email: $(gh api user --jq .notification_email)"
  [ -z "$(git config --global user.email)" ] && \
    git config --global user.email "$(gh api user --jq .notification_email)"
  echo "🟢 Configureing Git Editor: vim"
  [ -z "$(git config --global core.editor)" ] && \
    git config --global core.editor vim
  echo "🟢 Configureing Git Safe directories: *" 
  git config --global --add safe.directory '*'

  echo "🟢 GitHub configuration complete!"
}

# Update git repo remote for GitHub https pull and push. 
cloudGitHubFixRemote() {
  
  # Check if we're in a git repository
  if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "🔴 Not in a git repository"
    return 1
  fi

  # Get the current repository name from the directory
  local repo_name=$(basename "$(git rev-parse --show-toplevel)")
  
  # Get current remote URL to determine the organization/owner
  local current_remote=$(git remote get-url origin 2>/dev/null)
  local org_name="cloudorg"  # default organization
  
  # Try to extract organization from existing remote URL
  if [[ -n "$current_remote" ]]; then
    if [[ "$current_remote" =~ github\.com[:/]([^/]+)/([^/]+) ]]; then
      org_name="${BASH_REMATCH[1]}"
      echo "🟢 Detected organization: $org_name"
    fi
  fi
  
  # Allow override of organization name via parameter
  if [[ -n "$1" ]]; then
    org_name="$1"
    echo "🟢 Using specified organization: $org_name"
  fi
  
  local new_remote="https://github.com/${org_name}/${repo_name}.git"
  
  echo "🟢 Repository: $repo_name"
  echo "🟢 Organization: $org_name"
  echo "🟢 Setting remote to: $new_remote"
  
  # Update git remote
  if git remote get-url origin > /dev/null 2>&1; then
    git remote set-url origin "$new_remote" || {
      echo "🔴 Failed to update remote URL"
      return 1
    }
    echo "🟢 Updated existing remote origin"
  else
    git remote add origin "$new_remote" || {
      echo "🔴 Failed to add remote URL"
      return 1
    }
    echo "🟢 Added new remote origin"
  fi
  
  # Verify the change
  echo "🟢 Current remote: $(git remote get-url origin)"
  echo "🟢 Remote fix complete!"
}

# Fix remotes for all repositories in the repos directory
cloudGitHubFixAllRemotes() {
  local repos_dir="/workspaces/repos"
  local org_name="${1:-cloudorg}"
  
  if [[ ! -d "$repos_dir" ]]; then
    echo "🔴 Repos directory not found at $repos_dir"
    return 1
  fi
  
  echo "🟢 Fixing remotes for all repositories with organization: $org_name"
  echo "============================================================"
  
  local fixed=0
  local failed=0
  
  for repo in "$repos_dir"/*; do
    if [[ -d "$repo" && -d "$repo/.git" ]]; then
      local repo_name=$(basename "$repo")
      echo ""
      echo "📁 Processing: $repo_name"
      echo "----------------------------------------"
      
      cd "$repo"
      if cloudGitHubFixRemote "$org_name"; then
        ((fixed++))
      else
        ((failed++))
      fi
      cd - > /dev/null
    fi
  done
  
  echo ""
  echo "🟢 Summary: Fixed $fixed repositories, $failed failed"
}

# Show GitHub remote status for current repo
cloudGitHubRemoteStatus() {
  
  # Check if we're in a git repository
  if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "🔴 Not in a git repository"
    return 1
  fi
  
  local repo_name=$(basename "$(git rev-parse --show-toplevel)")
  echo "🟢 Repository: $repo_name"
  echo "----------------------------------------"
  
  # Show all remotes
  echo "📡 Remotes:"
  git remote -v
  
  # Show current branch and tracking info
  local branch=$(git branch --show-current 2>/dev/null || echo "unknown")
  echo "🌿 Current branch: $branch"
  
  # Check if branch has upstream
  if git rev-parse --abbrev-ref @{u} > /dev/null 2>&1; then
    local upstream=$(git rev-parse --abbrev-ref @{u})
    echo "🔗 Upstream: $upstream"
    
    # Check for unpushed commits
    local unpushed=$(git log @{u}..HEAD --oneline 2>/dev/null | wc -l)
    if [[ $unpushed -gt 0 ]]; then
      echo "📤 Unpushed commits: $unpushed"
    else
      echo "✅ Up to date with upstream"
    fi
  else
    echo "⚠️  No upstream branch set"
  fi
}

# Show GitHub remote status for all repositories
cloudGitHubAllRemoteStatus() {
  local repos_dir="/workspaces/repos"
  
  if [[ ! -d "$repos_dir" ]]; then
    echo "🔴 Repos directory not found at $repos_dir"
    return 1
  fi
  
  echo "🟢 GitHub remote status for all repositories:"
  echo "=============================================="
  
  for repo in "$repos_dir"/*; do
    if [[ -d "$repo" && -d "$repo/.git" ]]; then
      echo ""
      cd "$repo"
      cloudGitHubRemoteStatus
      cd - > /dev/null
    fi
  done
}