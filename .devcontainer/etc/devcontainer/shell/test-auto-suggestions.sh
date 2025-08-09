#!/bin/bash

#------------------------------------------------------------------------------#
# AUTO-SUGGESTIONS TEST SCRIPT                                                #
# ==========================================================================   #
# This script tests various auto-suggestion features to ensure they're        #
# working correctly in your terminal.                                         #
#------------------------------------------------------------------------------#

echo "🧪 Testing Auto-Suggestions and Completions"
echo "=============================================="
echo ""

# Test 1: Check if bash-completion is available
echo "🔍 Test 1: Bash Completion Availability"
if [ -f /usr/share/bash-completion/bash_completion ]; then
    echo "✅ bash-completion is installed and available"
else
    echo "❌ bash-completion not found"
fi
echo ""

# Test 2: Check readline settings
echo "🔍 Test 2: Readline Configuration"
echo "Current readline settings:"
bind -v | grep -E "(completion-ignore-case|show-all-if-ambiguous|colored-stats)" | head -5
echo ""

# Test 3: Check history settings
echo "🔍 Test 3: History Configuration"
echo "HISTSIZE: $HISTSIZE"
echo "HISTFILESIZE: $HISTFILESIZE"
echo "HISTCONTROL: $HISTCONTROL"
echo ""

# Test 4: Check if custom functions are available
echo "🔍 Test 4: Custom Function Availability"
functions_to_test=("cloudRepos" "cloudAWSProfile" "cloudGitHubFixRemote")
for func in "${functions_to_test[@]}"; do
    if declare -f "$func" > /dev/null; then
        echo "✅ $func is available"
    else
        echo "❌ $func not found"
    fi
done
echo ""

# Test 5: Check completion functions
echo "🔍 Test 5: Completion Functions"
if complete -p cloudRepos &>/dev/null; then
    echo "✅ cloudRepos completion is configured"
else
    echo "❌ cloudRepos completion not found"
fi

if complete -p git &>/dev/null; then
    echo "✅ git completion is configured"
else
    echo "❌ git completion not found"
fi
echo ""

# Test 6: Check if auto-suggestions script is loaded
echo "🔍 Test 6: Auto-suggestions Script Status"
if [[ "$-" == *i* ]]; then
    echo "✅ Running in interactive mode"
else
    echo "⚠️  Not running in interactive mode"
fi
echo ""

echo "📋 Manual Tests to Try:"
echo "----------------------"
echo "1. Type 'cloud' and press Tab twice to see function suggestions"
echo "2. Type 'git ' and press Tab to see git command completions"
echo "3. Type 'cd /work' and press Tab to complete to '/workspaces/'"
echo "4. Press Ctrl+R and type part of a previous command"
echo "5. Use arrow keys to navigate command history"
echo "6. Type 'cloudRepos ' and press Tab to see repo completions"
echo ""

echo "🎯 How to Use Auto-Suggestions:"
echo "------------------------------"
echo "• Tab - Complete current word"
echo "• Tab Tab - Show all possible completions"
echo "• Ctrl+R - Search command history"
echo "• Arrow Up/Down - Navigate history with search"
echo "• Alt+. - Insert last argument of previous command"
echo "• Just type directory name to cd into it (autocd)"
echo ""

echo "✨ Auto-suggestions test completed!"
echo "If any tests failed, try reloading your shell or rebuilding the container."
