#!/bin/sh

check_repo() {
  dir="$1"
  echo "============================================================"
  echo "Repository: $dir"
  (
    cd "$dir" || exit
    git fetch
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u} 2>/dev/null)
    BASE=$(git merge-base @ @{u} 2>/dev/null)
    if [ -z "$REMOTE" ]; then
      echo "No upstream configured, skipping pull"
    elif [ "$LOCAL" = "$REMOTE" ]; then
      if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
        echo "No remote changes, but you have uncommitted local changes:"
        git status --short
      else
        echo "Already up to date"
      fi
    elif [ "$LOCAL" = "$BASE" ]; then
      echo "Behind upstream..."
      if ! git diff --quiet || ! git diff --cached --quiet; then
        echo "Working tree is dirty, skipping pull to avoid conflicts"
        git status
      else
        echo "Pulling..."
        git pull
      fi
    elif [ "$REMOTE" = "$BASE" ]; then
      echo "Ahead of upstream, no pull needed"
      git status
    else
      echo "Diverged from upstream, manual intervention needed"
      git status
    fi
  )
}

# Status-only check: no fetch, no pull, just report local state
status_only() {
  dir="$1"
  echo "============================================================"
  echo "Repository (status only): $dir"
  (
    cd "$dir" || exit
    if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
      echo "Uncommitted local changes:"
      git status --short
    else
      echo "Clean working tree (no remote check performed)"
    fi
  )
}

check_repo ~/configfiles
check_repo ~/Documents/templates
check_repo ~/Documents/website
check_repo ~/claudedocs

# Sublime Text: status only, never auto-anything
# Replace the path below with whatever stfolder resolves to
status_only ~/Library/Application\ Support/Sublime\ Text/Packages/User

echo "Done."