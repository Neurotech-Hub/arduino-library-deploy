import os
import requests
import semver
import sys

# Get inputs
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
pr_version = os.getenv('pr_version')
main_version = os.getenv('main_version')

# GitHub API URL to merge PR
GITHUB_API_URL = f'https://api.github.com/repos/{os.getenv("GITHUB_REPOSITORY")}/pulls/{os.getenv("PR_NUMBER")}/merge'

import semver

def validate_version(pr_version, main_version):
    try:
        # Ensure versions are valid semantic versions
        semver.parse(pr_version)
        semver.parse(main_version)
    except ValueError:
        print(f"Error: One of the versions ({pr_version} or {main_version}) is not a valid semantic version.")
        sys.exit(1)

    # Parse version parts
    pr_major, pr_minor, pr_patch, pr_prerelease, _ = semver.parse_version_info(pr_version)
    main_major, main_minor, main_patch, _, _ = semver.parse_version_info(main_version)

    # Ensure PR version is greater than the main version
    if semver.compare(pr_version, main_version) <= 0:
        print(f"Error: PR version ({pr_version}) must be greater than main version ({main_version}).")
        sys.exit(1)

    # Major version increment: minor and patch must reset to 0
    if pr_major > main_major:
        if pr_minor != 0 or pr_patch != 0:
            print("Error: Major version increment requires MINOR and PATCH to reset to 0.")
            sys.exit(1)

    # Minor version increment: patch must reset to 0
    elif pr_minor > main_minor:
        if pr_patch != 0:
            print("Error: Minor version increment requires PATCH to reset to 0.")
            sys.exit(1)

    # Patch increment: must be sequential
    elif pr_patch != main_patch + 1:
        print(f"Error: Patch version increment must be sequential. Current patch: {main_patch}, PR patch: {pr_patch}.")
        sys.exit(1)

    # Pre-release validation (if applicable)
    if pr_prerelease:
        print(f"Warning: PR version ({pr_version}) includes a pre-release tag. This is acceptable if intended.")
    
    print(f"Version {pr_version} is valid.")

# Function to merge PR
def merge_pr():
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
    }

    data = {
        'commit_title': f'Merge PR #{os.getenv("PR_NUMBER")} - {os.getenv("PR_TITLE")}',
        'merge_method': 'squash'
    }

    response = requests.put(GITHUB_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Successfully merged PR #{os.getenv('PR_NUMBER')}")
    else:
        print(f"Error merging PR: {response.content}")
        sys.exit(1)

# Function to create release
def create_release():
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
    }

    release_data = {
        'tag_name': f'v{pr_version}',
        'release_name': f'Release v{pr_version}',
        'body': f'Changelog:\n- Updated to version {pr_version}',
        'draft': False,
        'prerelease': False
    }

    release_url = f'https://api.github.com/repos/{os.getenv("GITHUB_REPOSITORY")}/releases'
    response = requests.post(release_url, headers=headers, json=release_data)

    if response.status_code == 201:
        print(f"Release v{pr_version} created successfully.")
    else:
        print(f"Error creating release: {response.content}")
        sys.exit(1)

# Main function
def main():
    print(f"Validating version {pr_version} against main version {main_version}...")
    validate_version(pr_version, main_version)

    print("Merging the pull request...")
    merge_pr()

    print("Creating GitHub release...")
    create_release()

if __name__ == "__main__":
    main()
