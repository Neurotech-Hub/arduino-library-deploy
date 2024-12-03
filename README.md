# GitHub Action: Check Library Version, Merge PR, and Create Release

## Overview

This GitHub Action automates the process of checking the version in a pull request, comparing it with the version in the main branch, and performing actions based on the comparison. If the version in the pull request differs from the version in the main branch, the action will:

1. **Merge the Pull Request**: If the version differs, the pull request is automatically merged.
2. **Create a Release**: A GitHub release is created with the version from the pull request.

This action is ideal for Arduino library repositories where version management is important, ensuring that every pull request is checked for version consistency and is merged automatically if valid.

## Features

- **Version Checking**: Compares the version specified in `library.properties` of the pull request with the version in the `main` branch.
- **Pull Request Merging**: Automatically merges pull requests with a new version number.
- **Release Creation**: Automatically creates a GitHub release with the specified version.

## Inputs

| Input              | Description                                                             | Required | Default                  |
|--------------------|-------------------------------------------------------------------------|----------|--------------------------|
| `GITHUB_TOKEN`     | GitHub token used to interact with the GitHub API for merging PRs and creating releases. | Yes      | `${{ secrets.GITHUB_TOKEN }}` |

## Outputs

This action does not have any direct outputs but performs the following tasks:
- Merges pull requests where the version is different from the main branch.
- Creates a GitHub release with the version from the pull request.

## Usage

This action is triggered on the `pull_request` event when a pull request is opened, synchronized, or reopened.

### Example Workflow

Here is an example of how to integrate this action into your workflow:

```yaml
name: Check Library Version, Merge PR, and Create Release

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  check-version-and-release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: Arduino Library Deploy
        uses: ktauchathuranga/arduino-library-deploy@v0.0.0
        with:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Explanation of the Workflow

1. **Checkout PR Code**: This step uses the `actions/checkout@v3` to clone the pull request code.
2. **Get Version from PR**: Extracts the version from the `library.properties` file in the pull request.
3. **Fetch Main Branch Version**: Checks out the `library.properties` file from the main branch to compare versions.
4. **Compare Versions**: Compares the version from the pull request with the version in the main branch. If they are the same, the workflow fails (exit status 1).
5. **Merge Pull Request**: If the versions differ, the pull request is automatically merged using the GitHub API.
6. **Create Release**: A GitHub release is created with the new version from the pull request.

## Requirements

- **GitHub Token**: Ensure that your repository has the `GITHUB_TOKEN` secret available. This token is automatically provided by GitHub for interacting with the repository API.

## License

This action is licensed under the MIT License. See the `LICENSE` file for more details.

## Contributing

Feel free to fork this project, make improvements, and submit pull requests. Contributions are always welcome!
