#!/bin/bash
# Entrypoint script for the GitHub Action

set -e

# Ensure GITHUB_TOKEN is passed as an argument
if [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: GITHUB_TOKEN is not set!"
  exit 1
fi

# Add the repository to Git's safe directory list
git config --global --add safe.directory /github/workspace

# Extract PR details from the event payload
PR_NUMBER=$(jq --raw-output .pull_request.number $GITHUB_EVENT_PATH)
PR_TITLE=$(jq --raw-output .pull_request.title $GITHUB_EVENT_PATH)
PR_VERSION=$(grep '^version=' library.properties | cut -d'=' -f2)
MAIN_VERSION=$(git fetch origin main && git checkout origin/main -- library.properties && grep '^version=' library.properties | cut -d'=' -f2)

# Install arduino-cli (if not already installed)
if ! command -v arduino-cli &> /dev/null
then
  echo "arduino-cli not found, installing..."
  apt-get update
  apt-get install -y arduino-cli
else
  echo "arduino-cli already installed"
fi

# Export variables for Python script
export GITHUB_TOKEN=$GITHUB_TOKEN
export PR_NUMBER
export PR_TITLE
export pr_version=$PR_VERSION
export main_version=$MAIN_VERSION
export GITHUB_REPOSITORY=$GITHUB_REPOSITORY

# Run the Python script
python3 /action/action.py
