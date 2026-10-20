# Course Builder GitHub storage

The Course Builder uses the existing `ZaphodBeeblebrox12/prototypeweb` repository on `my-new-branch`. No separate image repository is required.

## What gets saved

- Course Builder images are stored under `course-assets/` in this repository.
- Each saved course source snapshot is versioned at `course-source/builder-drafts/<course-slug>.json`. It contains the course manifest data and lesson Markdown, not embedded image bytes.
- Django/PostgreSQL continues to store operational drafts, review status, permissions and publication state.
- The learner-facing site continues to render published courses through the shared Django Learning Room template. Saving a draft does not publish it automatically.

## Configure the host

Set `ACADEMY_GITHUB_ASSET_TOKEN` in the Django service's environment to a GitHub token with **Contents: read and write** access to `ZaphodBeeblebrox12/prototypeweb`. Do not commit the token or expose it to browser JavaScript.

The configured repository and branch are intentionally fixed in Django settings to the existing application repository and `my-new-branch`, so Course Builder writes do not target `main`. If the token is missing, the Django database draft can still be saved, but the API response will explicitly report that the GitHub source snapshot was not synced. Image uploads use local private storage until the token is configured.

## Workflow

1. Edit the course in the Course Builder.
2. **Save draft** stores the working draft in Django and writes a versioned JSON source snapshot to GitHub.
3. **Preview** renders the saved course through the shared learner preview.
4. **Submit for review** stores the snapshot and opens the existing Academy review checklist.
5. An administrator publishes it through the existing review workflow; the public catalogue reads published Django course records.

This keeps source control, draft workflow and learner delivery in one application without creating per-course hand-coded HTML pages or a second repository.
