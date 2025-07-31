# How to Create a Release

This project uses a CI/CD pipeline that automatically creates a GitHub Release when a new version tag is pushed to the repository.

## Releasing Alpha v1

To create the `v1.0.0-alpha` release, follow these steps:

1.  Ensure your `main` branch is up-to-date with all the changes you want to include in the release.

    ```bash
    git checkout main
    git pull origin main
    ```

2.  Create a new git tag. For the alpha, we will use a pre-release identifier.

    ```bash
    git tag -a v1.0.0-alpha -m "NEXAPod Alpha v1 Release"
    ```

3.  Push the tag to the GitHub repository.

    ```bash
    git push origin v1.0.0-alpha
    ```

Once the tag is pushed, the `release` job in the `.github/workflows/ci.yml` pipeline will trigger. It will automatically:
- Build and publish the Docker images.
- Create a new "pre-release" on GitHub with the tag `v1.0.0-alpha`.
- Populate the release notes with a link to the onboarding documentation.

You can then go to the "Releases" section of the GitHub repository to see the newly created release.

