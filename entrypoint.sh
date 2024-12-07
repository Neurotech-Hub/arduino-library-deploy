#!/bin/bash

set -e

# Extract the GitHub token from inputs
GITHUB_TOKEN=$1

if [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: GitHub token is not provided. Please pass it as the first argument."
  exit 1
fi

# Ensure the workspace is marked as safe for Git
echo "Configuring Git safe directory..."
git config --global --add safe.directory /github/workspace

echo "Checking out PR code..."
git fetch origin pull/${GITHUB_REF#refs/pull/}/head:pr || {
  echo "Error: Failed to fetch the pull request branch."
  exit 1
}
git checkout pr || {
  echo "Error: Failed to check out the PR branch."
  exit 1
}

echo "Fetching PR version..."
if ! pr_version=$(grep '^version=' library.properties | cut -d'=' -f2); then
  echo "Error: Unable to fetch PR version from library.properties."
  exit 1
fi
echo "PR version: $pr_version"

echo "Fetching main branch version..."
git fetch origin main || {
  echo "Error: Failed to fetch the main branch."
  exit 1
}
git checkout origin/main -- library.properties || {
  echo "Error: Failed to check out library.properties from the main branch."
  exit 1
}
if ! main_version=$(grep '^version=' library.properties | cut -d'=' -f2); then
  echo "Error: Unable to fetch main branch version from library.properties."
  exit 1
fi
echo "Main version: $main_version"

echo "Validating versioning rules..."
IFS='.' read -r pr_major pr_minor pr_patch <<< "$pr_version"
IFS='.' read -r main_major main_minor main_patch <<< "$main_version"

# Semantic versioning validation
if [ "$pr_major" -lt "$main_major" ] || 
   { [ "$pr_major" -eq "$main_major" ] && [ "$pr_minor" -lt "$main_minor" ]; } || 
   { [ "$pr_major" -eq "$main_major" ] && [ "$pr_minor" -eq "$main_minor" ] && [ "$pr_patch" -le "$main_patch" ]; }; then
  echo "Error: PR version ($pr_version) is not valid. It must increment according to semantic versioning rules."
  exit 1
fi

if [ "$pr_major" -gt "$main_major" ] && { [ "$pr_minor" -ne 0 ] || [ "$pr_patch" -ne 0 ]; }; then
  echo "Error: Major version increment requires MINOR and PATCH to reset to 0."
  exit 1
fi

if [ "$pr_major" -eq "$main_major" ] && [ "$pr_minor" -gt "$main_minor" ] && [ "$pr_patch" -ne 0 ]; then
  echo "Error: Minor version increment requires PATCH to reset to 0."
  exit 1
fi

echo "Version $pr_version is valid."

echo "Merging Pull Request..."
PR_NUMBER=$(jq --raw-output .pull_request.number "$GITHUB_EVENT_PATH")
PR_TITLE=$(jq --raw-output .pull_request.title "$GITHUB_EVENT_PATH")

if [ -z "$PR_NUMBER" ] || [ -z "$PR_TITLE" ]; then
  echo "Error: Pull request number or title is missing."
  exit 1
fi

API_URL="https://api.github.com/repos/${GITHUB_REPOSITORY}/pulls/${PR_NUMBER}/merge"
merge_response=$(curl -s -o response.json -w "%{http_code}" -X PUT "${API_URL}" \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{"commit_title":"Merge PR #'"${PR_NUMBER}"' - '"${PR_TITLE}"'","merge_method":"squash"}')

if [ "$merge_response" -ne 200 ]; then
  echo "Error: Failed to merge pull request. Response:"
  cat response.json
  exit 1
fi
echo "Pull request #${PR_NUMBER} merged successfully."

echo "Creating GitHub release..."
RELEASE_URL="https://api.github.com/repos/${GITHUB_REPOSITORY}/releases"
release_response=$(curl -s -o response.json -w "%{http_code}" -X POST "${RELEASE_URL}" \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{
        "tag_name": "v'"${pr_version}"'",
        "name": "Release v'"${pr_version}"'",
        "body": "Updated to version '"${pr_version}"'"
      }')

if [ "$release_response" -ne 201 ]; then
  echo "Error: Failed to create release. Response:"
  cat response.json
  exit 1
fi

echo "Release created successfully!"
