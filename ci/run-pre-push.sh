#!/bin/bash

python3 ci/get_photos.py

if git diff --quiet src/data/photos.json; then
  echo "No changes to photos.json, skipping commit."
else
  git add src/data/photos.json
  git commit -m "Update photos.json"
  git push origin head
  git fetch
  git merge
fi

exit 0