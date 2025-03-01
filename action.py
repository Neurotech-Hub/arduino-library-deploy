import os
import requests
import semver
import sys
import re
from pathlib import Path
import subprocess

# Get inputs
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
pr_version = os.getenv('pr_version')
main_version = os.getenv('main_version')

GITHUB_API_URL = f'https://api.github.com/repos/{os.getenv("GITHUB_REPOSITORY")}/pulls/{os.getenv("PR_NUMBER")}/merge'

# Enhanced validation: library.properties validation
def validate_library_metadata():
    library_properties_path = Path("library.properties")

    if not library_properties_path.exists():
        print("Error: library.properties file is missing.")
        sys.exit(1)

    required_fields = ["name", "version", "author", "maintainer", "sentence", "paragraph", "category", "url"]
    with open(library_properties_path, "r") as file:
        content = file.read()

    for field in required_fields:
        if not re.search(f"^{field}=", content, re.MULTILINE):
            print(f"Error: Required field '{field}' is missing in library.properties.")
            sys.exit(1)

    print("library.properties validation passed.")

# Enhanced validation: dependency checks
def validate_dependencies():
    library_properties_path = Path("library.properties")

    with open(library_properties_path, "r") as file:
        content = file.read()

    # Find lines starting with "depends=" and split by comma
    dependencies_lines = [line.split("=")[1].strip() for line in content.splitlines() if line.startswith("depends=")]
    if dependencies_lines:
        print("Validating dependencies...")
        for dep_line in dependencies_lines:
            dependencies = [dep.strip() for dep in dep_line.split(",")]
            for dependency in dependencies:
                print(f"Checking dependency: {dependency}")
                # Basic validation for valid library names
                # Allow letters, numbers, underscores, spaces, and hyphens
                if not re.match(r"^[a-zA-Z0-9_ -]+$", dependency):
                    print(f"Error: Invalid dependency format: {dependency}")
                    sys.exit(1)
        print("All dependencies are valid.")
    else:
        print("No dependencies found.")

# Semantic version validation (unchanged from original)
def validate_version(pr_version, main_version):
    try:
        semver.parse(pr_version)
        semver.parse(main_version)
    except ValueError:
        print(f"Error: One of the versions ({pr_version} or {main_version}) is not a valid semantic version.")
        sys.exit(1)

    pr_major, pr_minor, pr_patch, pr_prerelease, _ = semver.parse_version_info(pr_version)
    main_major, main_minor, main_patch, _, _ = semver.parse_version_info(main_version)

    if semver.compare(pr_version, main_version) <= 0:
        print(f"Error: PR version ({pr_version}) must be greater than main version ({main_version}).")
        sys.exit(1)

    if pr_major > main_major:
        if pr_minor != 0 or pr_patch != 0:
            print("Error: Major version increment requires MINOR and PATCH to reset to 0.")
            sys.exit(1)

    elif pr_minor > main_minor:
        if pr_patch != 0:
            print("Error: Minor version increment requires PATCH to reset to 0.")
            sys.exit(1)

    elif pr_patch != main_patch + 1:
        print(f"Error: Patch version increment must be sequential. Current patch: {main_patch}, PR patch: {pr_patch}.")
        sys.exit(1)

    if pr_prerelease:
        print(f"Warning: PR version ({pr_version}) includes a pre-release tag. This is acceptable if intended.")

    print(f"Version {pr_version} is valid.")

# Function to merge PR (unchanged from original)
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

# Function to create release (unchanged from original)
def create_release():
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
    }

    release_data = {
        'tag_name': f'v{pr_version}',
        'name': f'Release v{pr_version}',
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

    print("Validating library metadata...")
    validate_library_metadata()

    print("Validating dependencies...")
    validate_dependencies()

    print("Merging the pull request...")
    merge_pr()

    print("Creating GitHub release...")
    create_release()

if __name__ == "__main__":
    main()
