# Temporary GitHub storage for course images

The Academy's `course_asset_storage` can store new course-builder and lesson images in a **separate private GitHub repository**. PostgreSQL continues to store course/draft metadata and asset names. Django continues to deliver images through its authenticated, permission-checked routes; the browser never receives a GitHub token or a direct GitHub file URL.

## Configure it

1. Create a dedicated **private** repository for course assets. Do not use a public repository and do not use the application source repository for uploaded images.
2. Create a fine-grained personal access token limited to that one repository, with **Contents: Read and write**. Store it only in your hosting environment's secret/environment-variable settings.
3. Ensure the configured branch exists (the default is `main`).
4. Set these environment variables for the Django service:

| Variable | Example / default | Purpose |
| --- | --- | --- |
| `ACADEMY_GITHUB_ASSET_REPOSITORY` | `your-account/private-course-assets` | Private repository in `owner/repo` form |
| `ACADEMY_GITHUB_ASSET_TOKEN` | Secret value | Fine-grained token; never commit it |
| `ACADEMY_GITHUB_ASSET_BRANCH` | `main` | Existing branch to receive asset commits |
| `ACADEMY_GITHUB_ASSET_PATH_PREFIX` | `course-assets` | Directory prefix within that repository |
| `ACADEMY_GITHUB_ASSET_TIMEOUT` | `15` | HTTP timeout in seconds |

If the repository and token are not both configured, storage stays on the local private filesystem. Local reads are also attempted when a GitHub object is absent, which supports gradual migration of older local files.

## Operational notes

- GitHub's Contents API creates a commit when an image is saved or deleted. Multi-image drafts therefore create multiple asset commits; this is a temporary bridge, not a high-volume media architecture.
- Keep the repository private and restrict token access to it. Never put the token in JavaScript, browser requests, course Markdown, or committed settings.
- The application validates image MIME/type and upload size before storage, and serves assets through Django's protected endpoints. Do not expose GitHub `download_url` values.
- Deleting an asset through Django removes the corresponding GitHub file, creating another commit. Git history can retain old binary contents, so periodically review repository growth and retention.
- No hosting configuration or deployment is performed by this code change. After setting the environment variables, test draft save/reopen, multiple images, authorized delivery, and unauthorized access before relying on it.
- Later, the storage backend can be replaced with object storage without changing the course-builder API or asset metadata model.
