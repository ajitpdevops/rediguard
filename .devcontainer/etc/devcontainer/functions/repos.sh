#------------------------------------------------------------------------------#
# REPOS HELPER FUNCTIONS                                                      #
# This file contains utility functions for working with repositories          #
#------------------------------------------------------------------------------#

# Function: cloudRepos
# Description: Navigate to the mounted repos directory and optionally open a specific repo
# Usage: cloudRepos [repo-name]
cloudRepos() {
  local repo_name=$1
  local repos_dir="/workspaces/repos"
  
  if [[ ! -d "$repos_dir" ]]; then
    echo "🔴 Repos directory not found at $repos_dir"
    echo "💡 Setup instructions:"
    echo "   1. Set environment variable: export cloud_REPOS_PATH='/path/to/your/repos'"
    echo "   2. Or copy: cp .devcontainer/devcontainer.env.template .devcontainer/devcontainer.env"
    echo "   3. Edit the .env file with your repos path"
    echo "   4. Rebuild the devcontainer"
    echo "📖 See .devcontainer/SETUP.md for detailed instructions"
    return 1
  fi
  
  if [[ -z "$repo_name" ]]; then
    echo "🟢 Available repositories:"
    ls -1 "$repos_dir" 2>/dev/null || echo "🔴 No repositories found"
    echo "🟢 Navigate to repos: cd $repos_dir"
    cd "$repos_dir"
  else
    local target_dir="$repos_dir/$repo_name"
    if [[ -d "$target_dir" ]]; then
      echo "🟢 Navigating to: $target_dir"
      cd "$target_dir"
    else
      echo "🔴 Repository '$repo_name' not found in $repos_dir"
      echo "🟢 Available repositories:"
      ls -1 "$repos_dir" 2>/dev/null || echo "🔴 No repositories found"
      return 1
    fi
  fi
}

# Function: cloudReposList
# Description: List all available repositories with details
# Usage: cloudReposList
cloudReposList() {
  local repos_dir="/workspaces/repos"
  
  if [[ ! -d "$repos_dir" ]]; then
    echo "🔴 Repos directory not found at $repos_dir"
    return 1
  fi
  
  echo "🟢 Available repositories in $repos_dir:"
  echo "----------------------------------------"
  
  for repo in "$repos_dir"/*; do
    if [[ -d "$repo" ]]; then
      local repo_name=$(basename "$repo")
      echo "📁 $repo_name"
      
      # Check if it's a git repository
      if [[ -d "$repo/.git" ]]; then
        cd "$repo"
        local branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        local remote=$(git remote get-url origin 2>/dev/null || echo "no remote")
        echo "   🌿 Branch: $branch"
        echo "   🔗 Remote: $remote"
        cd - > /dev/null
      else
        echo "   ⚠️  Not a git repository"
      fi
      echo ""
    fi
  done
}

# Function: cloudReposCode
# Description: Open a repository in VS Code
# Usage: cloudReposCode <repo-name>
cloudReposCode() {
  local repo_name=$1
  local repos_dir="/workspaces/repos"
  
  if [[ -z "$repo_name" ]]; then
    echo "🟡 Usage: cloudReposCode <repo-name>"
    echo "🟢 Available repositories:"
    ls -1 "$repos_dir" 2>/dev/null || echo "🔴 No repositories found"
    return 1
  fi
  
  local target_dir="$repos_dir/$repo_name"
  if [[ -d "$target_dir" ]]; then
    echo "🟢 Opening $repo_name in VS Code..."
    code "$target_dir"
  else
    echo "🔴 Repository '$repo_name' not found in $repos_dir"
    echo "🟢 Available repositories:"
    ls -1 "$repos_dir" 2>/dev/null || echo "🔴 No repositories found"
    return 1
  fi
}

# Function: cloudReposStatus
# Description: Show git status for all repositories
# Usage: cloudReposStatus
cloudReposStatus() {
  local repos_dir="/workspaces/repos"
  
  if [[ ! -d "$repos_dir" ]]; then
    echo "🔴 Repos directory not found at $repos_dir"
    return 1
  fi
  
  echo "🟢 Git status for all repositories:"
  echo "==================================="
  
  for repo in "$repos_dir"/*; do
    if [[ -d "$repo" && -d "$repo/.git" ]]; then
      local repo_name=$(basename "$repo")
      echo ""
      echo "📁 $repo_name"
      echo "----------------------------------------"
      cd "$repo"
      
      # Get current branch
      local branch=$(git branch --show-current 2>/dev/null || echo "unknown")
      echo "🌿 Branch: $branch"
      
      # Check for uncommitted changes
      if [[ -n $(git status --porcelain) ]]; then
        echo "⚠️  Uncommitted changes:"
        git status --short
      else
        echo "✅ Working directory clean"
      fi
      
      # Check for unpushed commits
      local unpushed=$(git log @{u}..HEAD --oneline 2>/dev/null | wc -l)
      if [[ $unpushed -gt 0 ]]; then
        echo "📤 $unpushed unpushed commit(s)"
      fi
      
      cd - > /dev/null
    fi
  done
}
