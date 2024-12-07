# GitHub Action: Library Version Validation, Pull Request Automation, and Release Creation  

## Overview  

This GitHub Action simplifies version management and release workflows for Arduino library repositories. It ensures your library versions adhere to semantic versioning, automates version validation, merges valid pull requests, and creates releases.  

When the pull request version passes all validation checks, the action will:  

1. **Validate the Version**: Confirms the version progression follows semantic versioning and is logically correct compared to the current version.  
2. **Merge the Pull Request**: Automatically merges the pull request upon successful validation.  
3. **Create a Release**: Generates a GitHub release for the validated version, ensuring seamless deployment.  

This action is specifically designed for maintaining consistency and correctness in Arduino library repositories.  

---  

## Features  

- **Semantic Version Validation**: Ensures pull request versions follow semantic versioning conventions and differ from the current version.  
- **Automated Merging**: Automatically merges pull requests with valid versions, reducing manual intervention.  
- **Release Automation**: Creates GitHub releases with the validated version, including release notes and changelogs.  
- **Error Handling**: Rejects pull requests with invalid, duplicate, or incorrectly incremented versions, ensuring version integrity.  

---  

## Inputs  

| Input              | Description                                                             | Required | Default                  |  
|--------------------|-------------------------------------------------------------------------|----------|--------------------------|  
| `GITHUB_TOKEN`     | GitHub token for API access to merge pull requests and create releases. | Yes      | `${{ secrets.GITHUB_TOKEN }}` |  

---  

## Outputs  

This action does not return direct outputs but performs the following actions:  

- Validates the pull request version against semantic versioning rules.  
- Rejects invalid or duplicate versions.  
- Merges valid pull requests.  
- Generates a new GitHub release.  

---  

## Usage  

This action is triggered by the `pull_request` event whenever a pull request is opened, updated, or reopened.  

### Example Workflow  

Below is an example of a workflow using this GitHub Action:  

```yaml  
name: Validate Library Version and Create Release  

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
      - name: Checkout Code  
        uses: actions/checkout@v3  

      - name: Arduino Library Deploy  
        uses: ktauchathuranga/arduino-library-deploy@v2.1.3  
        env:  
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  
```  

---

## Workflow Steps  

1. **Checkout Code**: The workflow uses `actions/checkout@v3` to clone the pull request branch for inspection.  
2. **Version Extraction**: Extracts the `version` field from the `library.properties` file in the pull request.  
3. **Compare Versions**: Retrieves the version from the `main` branch and validates the progression of the pull request version:  
   - Ensures the new version is greater than the current one.  
   - Checks compliance with semantic versioning.  
4. **Merge and Release**:  
   - Merges the pull request if the version is valid.  
   - Creates a GitHub release with the validated version.  

---

## Semantic Versioning Rules  

This action enforces strict adherence to [Semantic Versioning (SemVer)](https://semver.org) rules:  

1. **Version Format**: Versions must follow the format `v<MAJOR>.<MINOR>.<PATCH>` (e.g., `v1.0.0`).  
2. **Version Progression**:  
   - **MAJOR**: Incremented for breaking changes, resetting `MINOR` and `PATCH` to `0`.  
   - **MINOR**: Incremented for new features, resetting `PATCH` to `0`.  
   - **PATCH**: Incremented for bug fixes.  
3. **Valid Changes Only**:  
   - A new version must be greater than the current one.  
   - Skipping intermediate versions without justification is disallowed (e.g., `v1.0.0` → `v1.0.2` without `v1.0.1` is invalid).  
4. **Pre-release Versions**: Supports pre-release identifiers (e.g., `v1.0.0-alpha`) for testing purposes.  

### Invalid Examples  

- **Backward progression**: `v1.0.0` following `v2.0.0`.  
- **Non-sequential patch increment**: `v1.0.0` → `v1.0.2` without `v1.0.1`.  
- **Improper reset**: `v2.0.1` following a major increment (`v1.0.0`).  

---

## Requirements  

- **GitHub Token**: A `GITHUB_TOKEN` must be provided in your repository secrets. This is automatically available in GitHub-hosted runners for API interactions.  

---  

## License  

This project is licensed under the MIT License. For more information, see the [LICENSE](LICENSE) file.  

---  

## Contributing  

Contributions are welcome! If you have ideas for improvement, feel free to fork the repository, create a new branch, and submit a pull request. Every contribution helps make this action better for the Arduino community.  
