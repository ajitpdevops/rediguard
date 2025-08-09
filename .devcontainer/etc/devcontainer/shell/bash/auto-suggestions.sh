#!/bin/bash

#------------------------------------------------------------------------------#
# AUTO-SUGGESTIONS AND ENHANCED COMPLETION SETUP                              #
# ==========================================================================   #
# This script sets up advanced auto-suggestions and command completion        #
# features to enhance the terminal experience.                                #
#------------------------------------------------------------------------------#

# Enable enhanced bash completion
if ! shopt -oq posix; then
  # Enable programmable completion features
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

# Configure readline for better command line editing
# Enable case-insensitive completion
bind "set completion-ignore-case on"

# Show all completions immediately if ambiguous
bind "set show-all-if-ambiguous on"

# Enable menu-complete (cycle through completions with Tab)
bind "set menu-complete-display-prefix on"

# Use colors for completion
bind "set colored-stats on"
bind "set colored-completion-prefix on"

# Show file type indicators (/, @, =, etc.)
bind "set visible-stats on"

# Append slash to directory names
bind "set mark-directories on"
bind "set mark-symlinked-directories on"

# Enable incremental history search
bind '"\e[A": history-search-backward'
bind '"\e[B": history-search-forward'

# Ctrl+R for reverse history search (enhanced)
bind '"\C-r": reverse-search-history'

# Alt+. to insert last argument of previous command
bind '"\e.": yank-last-arg'

# Enhanced history settings
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoreboth:erasedups  # Ignore duplicates and lines starting with space
export HISTIGNORE="ls:ll:la:cd:pwd:exit:clear:history"  # Ignore common commands
export HISTTIMEFORMAT="%Y-%m-%d %H:%M:%S "  # Add timestamps to history

# Enable history expansion with space
bind Space:magic-space

# Append to history file instead of overwriting
shopt -s histappend

# Update history after each command
export PROMPT_COMMAND="history -a; history -c; history -r; $PROMPT_COMMAND"

# Enable extended globbing
shopt -s extglob

# Enable case-insensitive globbing
shopt -s nocaseglob

# Autocorrect minor typos in directory names
shopt -s cdspell
shopt -s dirspell

#------------------------------------------------------------------------------#
# CUSTOM COMPLETION FUNCTIONS                                                 #
#------------------------------------------------------------------------------#

# Completion for cd command to include only directories
_cd_completion() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=($(compgen -d -- "$cur"))
}
complete -F _cd_completion cd

# Enhanced git completion
if [ -f /usr/share/bash-completion/completions/git ]; then
    source /usr/share/bash-completion/completions/git
fi

# Docker completion
if command -v docker >/dev/null 2>&1; then
    if [ -f /usr/share/bash-completion/completions/docker ]; then
        source /usr/share/bash-completion/completions/docker
    fi
fi

# Terraform completion
if command -v terraform >/dev/null 2>&1; then
    complete -C terraform terraform
fi

#------------------------------------------------------------------------------#
# SMART DIRECTORY NAVIGATION                                                  #
#------------------------------------------------------------------------------#

# Enable auto_cd (just type directory name to cd into it)
shopt -s autocd 2>/dev/null || true

# CDPATH for quick navigation to common directories
export CDPATH=".:~:/workspaces:/workspaces/repos"

#------------------------------------------------------------------------------#
# ENHANCED AUTO-SUGGESTIONS                                                   #
#------------------------------------------------------------------------------#

# Function to provide command suggestions based on history
_command_suggestions() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local suggestions

    # Get suggestions from history
    suggestions=$(history | grep -i "^[[:space:]]*[0-9]*[[:space:]]*$cur" | tail -10 | cut -c 8- | sort -u)

    # Add common commands if no history matches
    if [[ -z "$suggestions" ]]; then
        case "$cur" in
            git*)
                suggestions="git status\ngit add\ngit commit\ngit push\ngit pull\ngit log\ngit branch"
                ;;
            docker*)
                suggestions="docker ps\ndocker images\ndocker run\ndocker build\ndocker logs\ndocker exec"
                ;;
            aws*)
                suggestions="aws s3 ls\naws ec2 describe-instances\naws sts get-caller-identity"
                ;;
            cloud*)
                suggestions="cloudAWSLogin\ncloudAWSProfile\ncloudRepos\ncloudReposList\ncloudGitHubLogin"
                ;;
        esac
    fi

    COMPREPLY=($(compgen -W "$suggestions" -- "$cur"))
}

# Enable completion for empty commands (suggest based on history)
complete -F _command_suggestions ""

#------------------------------------------------------------------------------#
# COMMAND ALIASES FOR BETTER AUTO-COMPLETION                                  #
#------------------------------------------------------------------------------#

# Create aliases that work well with completion
alias l='ls -CF'
alias la='ls -A'
alias ll='ls -alF'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Git aliases with completion
alias g='git'
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git pull'
alias gd='git diff'
alias gb='git branch'
alias gco='git checkout'

# Enable completion for git aliases
complete -o default -o nospace -F _git g
complete -o default -o nospace -F _git_status gs
complete -o default -o nospace -F _git_add ga
complete -o default -o nospace -F _git_commit gc
complete -o default -o nospace -F _git_push gp
complete -o default -o nospace -F _git_pull gl
complete -o default -o nospace -F _git_diff gd
complete -o default -o nospace -F _git_branch gb
complete -o default -o nospace -F _git_checkout gco

# AWS CLI aliases
alias awsp='cloudAWSProfile'
alias awsl='cloudAWSLogin'

# Repository navigation aliases
alias repos='cloudRepos'
alias rlist='cloudReposList'

echo "🟢 Enhanced auto-suggestions and completions loaded!"