import os
import sys
import subprocess
import requests
import semver
import json

# GitHub API token
GITHUB_TOKEN = sys.argv[1]
REPO = os.getenv("GITHUB_REPOSITORY")
PULL_REQUEST_NUMBER = os.getenv("PR_NUMBER")
PULL_REQUEST_TITLE = os.getenv("PR_TITLE")

def get_version_from_property(file_name):
    with open(file_name, 'r') as f:
        for line in f:
            if line.startswith("version="):
                return line.split('=')[1].strip()

def fetch_git_version():
    subprocess.run(["git", "fetch", "origin"], check=True)
    subprocess.run(["git", "checkout", "origin/main", "--", "library.properties"], check=True)

def merge_pull_request():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PULL_REQUEST_NUMBER}/merge"
    data = {
        "commit_title": f"Merge PR #{PULL_REQUEST_NUMBER} - {PULL_REQUEST_TITLE}",
        "merge_method": "squash"
    }
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    response = requests.put(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print(f"Pull request #{PULL_REQUEST_NUMBER} merged successfully.")
    else:
        print(f"Failed to merge PR: {response.text}")
        sys.exit(1)

def create_github_release(version):
    url = f"https://api.github.com/repos/{REPO}/releases"
    data = {
        "tag_name": f"v{version}",
        "name": f"Release v{version}",
        "body": f"Updated to version {version}"
    }
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        print(f"Release v{version} created successfully.")
    else:
        print(f"Failed to create release: {response.text}")
        sys.exit(1)

def validate_version(pr_version, main_version):
    if semver.compare(pr_version, main_version) <= 0:
        print(f"Error: PR version ({pr_version}) is not valid. It must increment according to semantic versioning rules.")
        sys.exit(1)

    print(f"Version {pr_version} is valid.")

def main():
    # Get version from PR and main branch
    pr_version = get_version_from_property("library.properties")
    fetch_git_version()
    main_version = get_version_from_property("library.properties")

    print(f"PR version: {pr_version}")
    print(f"Main version: {main_version}")

    # Validate versioning rules
    validate_version(pr_version, main_version)

    # Merge PR if valid
    merge_pull_request()

    # Create GitHub Release
    create_github_release(pr_version)

if __name__ == "__main__":
    main()
