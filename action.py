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

# Function to validate the versioning rules
def validate_version(pr_version, main_version):
    pr_version_parts = pr_version.split('.')
    main_version_parts = main_version.split('.')

    pr_major, pr_minor, pr_patch = map(int, pr_version_parts)
    main_major, main_minor, main_patch = map(int, main_version_parts)

    if semver.compare(pr_version, main_version) <= 0:
        print(f"Error: PR version ({pr_version}) is not valid. It must increment according to semantic versioning rules.")
        sys.exit(1)

    if pr_major > main_major and (pr_minor != 0 or pr_patch != 0):
        print("Error: Major version increment requires MINOR and PATCH to reset to 0.")
        sys.exit(1)

    if pr_major == main_major and pr_minor > main_minor and pr_patch != 0:
        print("Error: Minor version increment requires PATCH to reset to 0.")
        sys.exit(1)

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
