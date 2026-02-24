#!/bin/sh

for dir in */ ; do
  [ -d "$dir" ] || continue

  echo "============================================================"
  echo "Directory: $dir"

  if [ -d "$dir/.git" ]; then
    (
      cd "$dir" || exit

      git fetch

      LOCAL=$(git rev-parse @)
      REMOTE=$(git rev-parse @{u} 2>/dev/null)
      BASE=$(git merge-base @ @{u} 2>/dev/null)

      if [ -z "$REMOTE" ]; then
        echo "No upstream configured, skipping pull"
      elif [ "$LOCAL" = "$REMOTE" ]; then
        echo "Already up to date"
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
  else
    echo "Not a git repository, skipping"
  fi

done

echo "Done."
