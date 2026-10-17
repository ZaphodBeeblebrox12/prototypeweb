# TradeThesis Course Manifest Standard

The canonical starter implementation is understand-bollinger-bands/course-manifest.json and uses schema_version: 1.

## Source rules

- Use the manifest as metadata/orchestration, not as a duplicate store of student lesson prose.
- Authored lesson text remains in Markdown files under the course package.
- Give each course, module and lesson a stable lowercase slug. Do not regenerate slugs from titles after a course has been imported; titles may be edited without changing the lesson identity.
- Each module defines a Markdown source path relative to the manifest folder.
- Each lesson's source_id must match a Markdown heading in the form: Lesson 1.1 — Lesson title. The title must match too. The importer rejects missing or mismatched lesson headings instead of silently importing a partial module.
- Every Markdown image reference becomes a stable asset slot. External HTTP(S) URLs are retained as the default image. A course administrator can upload a JPEG, PNG or WebP replacement to override that reference without editing Markdown. Missing local files remain visible as missing slots and require an uploaded replacement before publication.
- Notebook prompts are course-specific and can be overridden for a lesson.

## Deployment semantics

Imports are staged snapshots. They do not update the published Course, CourseModule or Lesson rows. An administrator inspects the staged snapshot, resolves missing assets, and explicitly publishes it. Re-importing the same content hash reuses the existing snapshot. Importing a changed snapshot supersedes prior pending review snapshots but leaves the currently published course untouched until publication.

Publication matches module and lesson records by stable slug. Existing UUIDs and learner progress records remain intact. No offer or entitlement is created automatically.
