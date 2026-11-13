# TradeThesis Course Builder: Structured editor rebuild

**Status:** Accepted for staged implementation  
**Decision:** Use Tiptap 3 (ProseMirror) as the editing engine; keep Django and the current Academy publishing and delivery systems.

## Why change the editor

The current visual editor edits HTML, serializes it back to Markdown, and relies on a separate learner renderer. The conversion boundary has already produced formatting regressions. The existing builder also stores course-level data, lesson prose, regional variants, figure metadata, tables, questions, videos, and instructor-only material through several distinct structures.

The replacement should make the lesson body a typed document tree. The editor, validation layer, and learner renderer will share a versioned contract. Markdown will remain an import/export and compatibility format, not the canonical editing state.

## Selected technology

Use the open-source Tiptap editor on top of ProseMirror:

- The editor is framework-agnostic and supports vanilla JavaScript with ES module bundling.
- Its JSON representation is a tree of typed nodes, text, marks, and attributes.
- Its extension system supports custom TradeThesis content blocks.
- The core editor is MIT-licensed. We will use only OSS packages for the initial rebuild; no Tiptap Cloud, Pro collaboration, managed conversion, or subscription-only product features are required.

References:
- [Tiptap vanilla JavaScript installation](https://tiptap.dev/docs/editor/getting-started/install/vanilla-javascript)
- [Tiptap document and schema concepts](https://tiptap.dev/docs/editor/core-concepts/schema)
- [Tiptap JSON document model](https://tiptap.dev/docs/editor/core-concepts/introduction)
- [Tiptap custom node extensions](https://tiptap.dev/docs/editor/extensions/custom-extensions/create-new/node)
- [Tiptap pricing and open-source platform distinction](https://tiptap.dev/pricing)

Tiptap's Markdown extension is not the source of truth. The canonical format is our versioned JSON document. We will own and test the Markdown import/export adapters because the current lesson syntax contains TradeThesis-specific reference tokens and metadata.

## Non-negotiable preservation rules

1. No existing course or lesson is rewritten as part of the initial rollout.
2. The existing `Lesson.content_markdown` and `Lesson.content_json` fields remain supported.
3. The structured document is additive and versioned; it is stored under `content_json.lesson_document`.
4. Existing Markdown remains the compatibility mirror until the learner renderer has a fully tested structured-document path.
5. Unknown nodes, marks, or versions must produce a visible compatibility error. They must never be silently stripped.
6. The old editor remains available as a fallback until parity and save/reopen tests pass.
7. Publishing, review, course pricing, entitlements, video security, and media storage remain in their existing Django services.

## Canonical document envelope

Version 1 is stored as:

```json
{
  "format": "tradethesis.lesson-document",
  "version": 1,
  "document": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": [
          { "type": "text", "text": "Example", "marks": [{ "type": "bold" }] }
        ]
      }
    ]
  }
}
```

The envelope is independent of `content_json.schema_version`. A document upgrade does not silently change unrelated lesson metadata.

The initial server contract is implemented in `apps/academy/lesson_document.py`; the shared JSON Schema lives at `apps/academy/schemas/lesson-document-v1.schema.json`.

## Feature preservation matrix

| Existing capability | Structured-editor representation | Existing system retained |
|---|---|---|
| Paragraphs and headings | paragraph / heading nodes | Markdown mirror |
| Bold, italic, underline, strike, inline code, links | text marks | Sanitized learner HTML |
| Bulleted and numbered / nested lists | list nodes and listItem nodes | Markdown mirror |
| Quotes and dividers | blockquote / horizontalRule | Markdown mirror |
| Fenced code and language | codeBlock with language attribute | Markdown mirror |
| Simple and complex tables | table, row, header and cell nodes; spans, alignment, widths | Existing table metadata until renderer parity |
| Images and figures | figure/image custom nodes with stable asset IDs | CourseMediaAsset / CourseImportAsset |
| Image groups and comparison cards | custom figure nodes referencing existing figure metadata | Existing `content_json.figures` |
| Course cards and lesson references | reference nodes containing stable IDs | Existing reference resolution |
| Regional content blocks and whole-lesson variants | regionalBlock reference nodes | Existing `regional_blocks` and `regional_lesson_content` |
| Practice questions | practiceQuestion reference nodes | public question data and instructor rubric remain separate |
| Notebook / reflection | dedicated structured block nodes | existing notebook and reflection JSON |
| Video | videoBlock reference | CourseImportVideo / ProtectedLessonVideo pipeline |
| Instructor answer keys and rubrics | not embedded in learner document | LessonInstructorMaterial remains private |

A content type is not considered migrated until it can be opened, edited, saved, reopened, previewed, and published without loss.

## Data flow during migration

### Transitional phase

- The Tiptap document is the editing source of truth for lessons using the new editor.
- The Markdown field is generated as a compatibility export and remains available to existing import, review, and learner-rendering code.
- Structured references keep stable IDs; asset bytes, answer keys, and protected media secrets are never embedded in the document.
- The server validates the envelope and version before accepting it.

### Final phase

- The learner renderer consumes the same canonical document model through a server-side renderer.
- Markdown is only an import/export format and source backup.
- Old Markdown-only lessons remain readable indefinitely through a legacy adapter.
- Conversion to structured JSON is lazy or explicitly batched, not a mandatory one-time database rewrite.

## Implementation phases

### Phase 1 — contract and safe storage (current)

- Add the versioned envelope, validation, and JSON Schema.
- Persist the document additively beside Markdown in the existing JSON fields.
- Hydrate it when an existing published course is opened for editing.
- Add validation tests, unknown-node rejection, and legacy no-document behavior.
- No database migration and no learner-facing behavior change.

### Phase 2 — Tiptap editor shell

- Add a pinned, self-hosted browser bundle using the Render Python build's available Node/npm tooling.
- Create a separate editor mount with TradeThesis toolbar, contextual table actions, keyboard shortcuts, selection preservation, autosave state, and mobile behavior.
- Keep the new editor behind a staff-only route/feature flag.
- Start with text, headings, marks, lists, quotes, code, links, and tables.

### Phase 3 — TradeThesis content extensions

Implement and test figure, image group, comparison card, course card, lesson reference, regional block, practice question, video, notebook, reflection, and lesson-tab nodes. Each extension uses stable IDs and references existing services.

### Phase 4 — adapters and parity

- Implement tested Markdown-to-document and document-to-Markdown adapters.
- Round-trip old lessons without stripping unsupported content.
- Add browser-level save/reopen and learner-preview tests.
- Ensure the server and learner renderer agree on every supported node.

### Phase 5 — controlled rollout

- Enable only for staff and test drafts.
- Compare editor output with learner preview for representative courses.
- Expand to selected drafts only after acceptance tests pass.
- Retain legacy editor fallback and rollback path for at least one release cycle.

### Phase 6 — retire duplicate code

Only after telemetry and regression tests show no remaining callers:
- Remove the old HTML/Markdown editing surface.
- Remove obsolete selection and serializer code.
- Keep the Markdown import/export adapter and legacy learner renderer for old lessons.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Old Markdown features have no Tiptap equivalent | Preserve each unsupported block as an explicit legacyMarkdown node; prohibit destructive edits until a custom node exists |
| Regional variants or figures lose stable references | Store stable IDs in nodes; retain current regional and asset records |
| Learner output differs from editor | Use one schema, explicit server renderer, and editor-to-learner visual parity tests |
| Old editor overwrites a newer document | Server-side document carry-forward and revision/conflict checks |
| Large lessons or complex tables degrade editor performance | Node-count/depth limits, lazy media hydration, performance tests |
| New extension data is invalid or unsafe | Strict schema/version/URL validation and unknown-node rejection |
| Deployment breaks the existing editor | Feature flag, separate route, bundled assets, old route remains the fallback |

## Acceptance criteria before replacing the current editor

- A representative existing lesson opens without content changes.
- Every feature in the preservation matrix has a conversion and save/reopen test.
- Unknown nodes are preserved or editing is blocked; nothing is silently removed.
- A draft can be saved, closed, reopened, and published with identical intended learner output.
- Figures, tables, regional variants, questions, and protected videos continue to resolve through existing stable IDs and services.
- Instructor-only answers and rubrics remain inaccessible to learner views.
- Existing legacy lessons continue to render without migration.
- The rollback switch is tested.

## Current scope

This implementation phase adds the document contract and safe additive storage only. It does not activate Tiptap for authors, rewrite any course, alter learner rendering, publish content, or deploy to production.


## Phase 2 prototype checkpoint — 5 November 2026

A separate staff-only Tiptap authoring lab is being introduced at
`/staff/course-builder/tiptap/`. It is protected by the existing
`is_course_content_admin` policy and the opt-in
`ACADEMY_TIPTAP_EDITOR_ENABLED` setting (default: false).

The first shell uses a self-hosted, version-pinned Tiptap 3 bundle and supports
basic text structure, marks, lists, quotations, code blocks, links, undo/redo,
and contextual table actions. It can export the v1 lesson-document envelope
as JSON for inspection.

This prototype is deliberately not connected to Course Builder draft saves,
published lessons, import/review, or learner rendering. It is a safe authoring
sandbox until the Markdown adapters, custom TradeThesis nodes, server save
contract, and browser round-trip tests are ready. The existing Course Builder
route and assets are not replaced.

To build the bundle, the deployment must have Node.js/npm and set
`ACADEMY_TIPTAP_EDITOR_ENABLED=true`. The CI workflow builds the bundle
independently. Do not enable the flag on staging until the deployment build
has completed successfully.


## Markdown adapter prototype note — 5 November 2026

The isolated authoring lab now includes an experimental Markdown import/export
panel using the open-source `@tiptap/markdown` extension, pinned to the same
Tiptap release as the editor. It is enabled only in the staff prototype and
is not used to save or migrate any existing lesson.

The upstream Markdown extension is currently beta. Its documented limitations
include unsupported comments and limited table-cell child content. Standard
Markdown/GFM import is useful for testing ordinary prose, but it is not our
production compatibility adapter. TradeThesis-specific markers (asset IDs,
figures, regional variants, course/lesson references, quizzes, notebooks,
reflections and video references) still require explicit custom parsing and
serialization. Until those adapters are tested, the legacy Markdown field
remains untouched and the import panel warns authors not to overwrite lessons.


The prototype now has Node-based DOM tests for ordinary Markdown formatting,
GFM tables, and preservation of the current plain-text TradeThesis reference
tokens. These tests run during the Academy CI bundle build.


The round-trip tests found that the generic Markdown serializer escapes
bracketed TradeThesis references (for example `[[regional-block:india]]`) in
its exported syntax. The marker's text survives re-import, but the escaped
Markdown is not currently executable by the existing learner resolver. A custom
TradeThesis Markdown spec is therefore required before any exported Markdown can
be used as the compatibility mirror.

## Phase 3 completion checkpoint — 5 November 2026

The isolated Tiptap editor now has the TradeThesis-specific extension registry and
sidecar reference adapter.

### Structured nodes

- Inline references: figure, image group, course card, lesson reference,
  regional content block, structured table reference and lesson-tab marker.
- Comparison-card figures are resolved to a distinct typed node.
- Asset-backed images retain stable `asset://UUID` references and display local
  placeholders; the editor never requests an asset URL during import.
- Sidecar-backed block nodes: practice question, protected video, notebook,
  reflection, callout, and whole-lesson regional variant.
- Unknown `[[...]]` markers remain explicit `legacyMarkdown` nodes.
- JSON-only blocks with no proven lossless Markdown representation refuse
  Markdown export rather than being dropped.

### Existing Academy sidecars

The adapter accepts either the current Course Builder lesson shape or the
published `Lesson.content_json` shape and indexes:

- Image metadata, stable assets, figures, image groups and comparison cards.
- Structured table rows and cell spans.
- Inline regional blocks and country/region whole-lesson alternatives.
- Public practice-question prompts/options and linked question images.
- Notebook prompts and reflection material.
- Protected-video record ID, staged/protected kind and status only.
- Existing course/lesson references and marker IDs.

Typed nodes carry stable IDs or audience keys; the existing sidecar stores keep
the underlying authoring data. Question answer keys/correct indices and question
explanations are excluded from the sidecar reference index. Reflection fields stay
in their separate reflection sidecar and are not copied into the learner document.
Private video file names, storage paths, HLS manifests, stream keys and
encryption details are never copied into the document. Missing or mismatched
references produce diagnostics, and adding sidecar-backed nodes is idempotent.

The protected-video builder metadata now includes the stable record ID and
record kind so the new document can reference staged or published media without
exposing any private media location. The versioned Python validator and shared
JSON Schema accept the whole-lesson regional-variant node.

### Validation coverage

The Node suite includes the complete Bollinger Bands course source package
(30 lessons, 62 image references and Markdown tables), TradeThesis marker
round-trips, unknown-marker preservation, sidecar hydration, stable-reference
resolution, regional variants, privacy boundaries and lossy-export refusal.
The existing Academy Django tests cover the staff-only route and protected-video
metadata contract.

### Phase boundary

Phase 3 provides the typed extension and sidecar-reference layer. It does not
connect the sandbox to live draft loading/saving, publishing, review or learner
rendering. Those are Phase 4 parity and integration tasks. The legacy Course
Builder remains the live editing path and is not modified or deployed by this
checkpoint.


## Phase 4 implementation checkpoint — 5 November 2026

The isolated staff Tiptap route now connects to saved Course Builder drafts through
a separate API. The existing /staff/course-builder/ route remains unchanged.

### Draft loading and saving

- The editor lists editable CourseImport drafts and loads one selected lesson
  at a time. It can open new drafts and saved revisions created through the
  existing Course Builder workflow.
- A lesson with no lesson_document is imported from its existing Markdown
  mirror. A supported v1 document is opened from content_json.lesson_document.
- The editor hydrates typed references from the existing image, figure, table,
  regional, question, notebook, reflection and protected-video records.
- Save writes the versioned JSON document into content_json.lesson_document
  and updates the Markdown compatibility mirror in the same CourseImport
  draft snapshot. It does not write to a live Course or Lesson row.
- The save request carries the draft's updated_at revision token. A stale tab
  receives HTTP 409 and cannot overwrite a newer save. A deleted, submitted or
  otherwise non-editable draft is rejected. Rejected drafts return to editable
  Draft status only after a successful save.
- Instructor answer keys and explanations are removed from the browser load
  response. They remain in their existing instructor-material payload.
- The browser and server both check sidecar references before accepting a save.
  Missing or mismatched assets, figures, tables, questions, video, notebook,
  reflection or regional references block the save.

### Preview and lifecycle parity

The editor exposes the existing Academy course-import-preview page for the
selected saved draft. That page uses the same learner lesson template and
legacy Academy renderer as the current published lesson view. It resolves the
saved Markdown compatibility mirror with the same figure/table/regional,
question, notebook, reflection and protected-video records.

Tiptap is not a publishing interface. Review, approval, publication, course
offers, pricing, access grants and protected-video processing remain in their
existing Academy services. The old Course Builder remains available as the
fallback. An administrator can first use its existing Edit published course
flow to create a reviewable draft, save it, and then open that saved revision
in the Tiptap preview route.

### Explicit compatibility limits

- Unknown legacyMarkdown markers keep their original token and can be saved
  without conversion to ordinary text.
- JSON-only question, protected-video, notebook, reflection and whole-lesson
  regional references stay in their respective existing Academy sidecars.
  Their document nodes are not serialized as fake learner Markdown.
- Callout nodes remain read-only: the existing Academy learner renderer has no
  corresponding callout component, so the browser and server block a save
  rather than omit callout content in the learner preview.
- Unknown document versions remain read-only until a compatible editor is
  available.

### Rollout boundary

Phase 4 is still a staff-only, opt-in preview. The feature flag remains off by
default. No database migration, automatic conversion of existing lessons,
staging/production deployment, direct edit of live lesson rows, publication,
or removal of the legacy editor is included in this checkpoint.

The Phase 4 acceptance tests cover draft listing, lesson load, private answer
key isolation, JSON/Markdown save, preserved sidecars, stale-revision rejection,
server-side reference validation and the existing Academy learner preview.



## Phase 5 implementation checkpoint — media integration

Phase 5 is being developed on the separate
`feature/course-builder-tiptap-phase5-media` branch. It remains an additive,
staff-only extension; it does not replace the legacy Course Builder or alter
production deployment configuration.

### Images

- Tiptap uses the existing `CourseImportAsset` model and configured Academy
  asset storage. It does not introduce a separate media bucket or storage
  provider.
- Draft image upload accepts JPEG, PNG and WebP, validates the actual image
  bytes, and enforces the existing 10 MB per-image limit.
- The draft media API lists images already attached to the saved draft and
  allows the editor to attach one to the selected lesson.
- The editor displays the existing authenticated Academy asset URL while
  editing. The runtime-only preview URL is stripped from the canonical
  lesson-document JSON and the Markdown mirror retains the stable
  `asset://UUID` reference.
- Upload and attach operations use the same draft revision token as lesson
  saves; stale media writes are rejected rather than silently overwriting
  newer draft work.

### Protected lesson videos

- The editor reuses the existing staff Course Builder protected-video upload
  endpoint and `CourseImportVideo` staging model.
- Source files continue through the private video storage configuration
  (Google Drive in the existing staging setup); the Tiptap editor does not
  expose source paths, manifests, stream keys or encryption material.
- The upload response includes the stable staged-video ID and updated draft
  revision so Tiptap can insert the sidecar reference without creating a
  false stale-save conflict.
- Tiptap supplies the draft revision token before and after the private upload;
  a stale upload is rejected and its unattached temporary file is discarded.
  The token remains optional for the legacy Course Builder endpoint.
- Protected-video references are validated against the staged record or the
  published `ProtectedLessonVideo` record, not a browser-supplied status.
- Encrypted HLS processing remains in the existing approval/publication
  pipeline. Uploading a file in a draft does not create a public playable URL.

### External video links

- A lesson can store an HTTP/HTTPS external video URL through the Tiptap media
  controls under the explicit `external_video_url` content key. The legacy
  `video_url` key remains gated by `ACADEMY_ALLOW_LEGACY_VIDEO_URLS`; the
  Tiptap path does not enable that compatibility setting.
- URLs are length-limited and reject unsupported schemes, missing hosts and
  embedded credentials.
- A protected video takes precedence over an external video URL. Direct
  individual-purchase entitlements do not receive the unprotected external
  URL; authors should upload a protected source for those lessons. Ordinary
  hyperlinks in lesson text remain supported.
- The existing Course Builder hydrates the explicit external URL when editing
  a published lesson and retains both the explicit and legacy content keys on
  save, so the two editors can coexist during the rollout.
- External links are not encrypted, watermarked or access-controlled by the
  Academy protected-video player.

### Phase 5 release boundary

The implementation is not production-ready until backend and Node CI pass,
the editor is manually exercised against the Bollinger Bands draft, image and
video delivery are confirmed in an authenticated preview, and stale-revision
handling is verified in two tabs. The legacy editor remains available
throughout evaluation. The feature branch is not merged or deployed to the
main staging or production services as part of this checkpoint.
