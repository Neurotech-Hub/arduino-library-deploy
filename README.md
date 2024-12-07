# GitHub Action: Check Library Version, Validate, Merge PR, and Create Release

## Overview

This GitHub Action streamlines the process of managing library versions in pull requests for Arduino projects. It automates the validation, merging, and release creation, ensuring your library versions adhere to semantic versioning standards and proper version progression.

If the version in the pull request meets the validation criteria, the action will:

1. **Validate the Version**: Ensures the version progression follows semantic versioning rules and is logically correct compared to the current version.
2. **Merge the Pull Request**: Automatically merges the pull request if the version is valid.
3. **Create a Release**: Generates a GitHub release with the validated version.

This action is perfect for Arduino library repositories where version consistency and correctness are critical.

## Features

- **Version Validation**: Checks that the pull request version differs from the main branch version and follows semantic versioning rules (e.g., v1.0.1 cannot follow v2.0.0).
- **Automated Pull Request Merging**: Automatically merges valid pull requests.
- **Release Creation**: Automatically creates a GitHub release with the pull request version.
- **Error Handling**: Rejects pull requests with invalid or duplicate versions.

## Inputs

| Input              | Description                                                             | Required | Default                  |
|--------------------|-------------------------------------------------------------------------|----------|--------------------------|
| `GITHUB_TOKEN`     | GitHub token used to interact with the GitHub API for merging PRs and creating releases. | Yes      | `${{ secrets.GITHUB_TOKEN }}` |

## Outputs

This action does not produce direct outputs but performs the following tasks:
- Validates version numbers and rejects invalid pull requests.
- Merges pull requests with a valid, new version.
- Creates a GitHub release with the new version.

## Usage

This action is triggered on the `pull_request` event when a pull request is opened, synchronized, or reopened.

### Example Workflow

Below is an example of how to use this action in your workflow:

```yaml
name: Check Library Version, Validate, Merge PR, and Create Release

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  validate-and-release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: Arduino Library Deploy
        uses: ktauchathuranga/arduino-library-deploy@v2.1.3
        with:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Explanation of the Workflow

1. **Checkout PR Code**: Uses `actions/checkout@v3` to clone the pull request code for inspection.
2. **Extract PR Version**: Retrieves the `version` field from `library.properties` in the pull request.
3. **Fetch Main Branch Version**: Checks out the main branch version of `library.properties` for comparison.
4. **Validate Version**: Ensures the pull request version is:
   - Different from the main branch version.
   - Progressing logically according to semantic versioning rules (e.g., v1.0.1 cannot follow v2.0.0).
   - Does not skip patch or minor versions inappropriately.
5. **Merge Pull Request**: If the version is valid, the pull request is automatically merged using the GitHub API.
6. **Create Release**: Generates a GitHub release with the pull request version, including a changelog.

## Version Validation Rules

- Versions must follow semantic versioning (`v<major>.<minor>.<patch>`).
- The pull request version must be greater than the current main branch version.
- Invalid cases include:
  - A smaller version number following a larger one (e.g., `v1.0.0` after `v2.0.0`).
  - Skipping intermediate patch or minor versions without justification (e.g., `v0.1.0` followed directly by `v0.1.3`).

## Requirements

- **GitHub Token**: Ensure your repository includes the `GITHUB_TOKEN` secret, which is automatically provided by GitHub for repository API interactions.

## License

This action is licensed under the MIT License. See the `LICENSE` file for more details.

## Contributing

We welcome contributions! Feel free to fork this project, suggest improvements, and submit pull requests. Your input helps enhance this action for everyone.
