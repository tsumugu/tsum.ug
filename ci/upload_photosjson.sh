#!/bin/bash

python3 ci/get_photos.py

git add photos.json
git commit -m "Update photos.json"