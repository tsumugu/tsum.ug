#!/bin/sh
python3 ci/get_photos.py

if git diff --quiet photos.json; then
  echo "No changes to photos.json, skipping commit."
else
  git add photos.json
  git commit -m "Update photos.json"
  git push origin head
fi

exit 0