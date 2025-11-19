#!/bin/bash

# go to the folder where repos.txt is
cd "repos"

# read repos.txt line by line
while IFS= read -r repo; do
  # skip empty lines or comments
  [ -z "$repo" ] && continue
  [[ "$repo" =~ ^# ]] && continue

  git clone "$repo"
done < top_repos_java.txt
