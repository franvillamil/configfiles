#!/bin/sh

for dir in */ ; do
  [ -d "$dir" ] || continue

  echo "============================================================"
  echo "Directory: $dir"

  if [ -d "$dir/.git" ]; then
    (
      cd "$dir" || exit

      git fetch && git status
    )
  else
    echo "Not a git repository, skipping"
  fi
done

echo "Done."
