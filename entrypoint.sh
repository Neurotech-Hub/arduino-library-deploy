#!/bin/bash

set -e

# Extract the GitHub token from inputs
GITHUB_TOKEN=$1

echo "Checking out PR code..."
git fetch origin pull/${GITHUB_REF#refs/pull/}/head:pr
git checkout pr

echo "Fetching PR version..."
pr_version=$(grep '^version=' library.properties | cut -d'=' -f2)
echo "PR version: $pr_version"

echo "Fetching main branch version..."
git fetch origin main
git checkout origin/main -- library.properties
main_version=$(grep '^version=' library.properties | cut -d'=' -f2)
echo "Main version: $main_version"

echo "Validating versioning rules..."
IFS='.' read -r pr_major pr_minor pr_patch <<< "$pr_version"
IFS='.' read -r main_major main_minor main_patch <<< "$main_version"

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
PR_NUMBER=$(jq --raw-output .pull_request.number $GITHUB_EVENT_PATH)
PR_TITLE=$(jq --raw-output .pull_request.title $GITHUB_EVENT_PATH)
API_URL="https://api.github.com/repos/${GITHUB_REPOSITORY}/pulls/${PR_NUMBER}/merge"
curl -X PUT "${API_URL}" \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{"commit_title":"Merge PR #'"${PR_NUMBER}"' - '"${PR_TITLE}"'","merge_method":"squash"}'

echo "Pull request #${PR_NUMBER} merged successfully."

echo "Creating GitHub release..."
RELEASE_URL="https://api.github.com/repos/${GITHUB_REPOSITORY}/releases"
curl -X POST "${RELEASE_URL}" \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{
        "tag_name": "v'"${pr_version}"'",
        "name": "Release v'"${pr_version}"'",
        "body": "Updated to version '"${pr_version}"'"
      }'

echo "Release created successfully!"
