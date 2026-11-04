# TradeThesis Course Builder — structured editor rebuild

## Decision

Rebuild the lesson-body editing engine on Tiptap (ProseMirror), while retaining Django, the existing Course Builder shell, course catalogue, pricing, review/approval workflow, asset storage, protected video pipeline, learner progress and existing course records.

This is an editor-engine replacement, not a rewrite of the Academy product.

Tiptap is framework-agnostic and its core is MIT-licensed. The project will pin the exact package set and ship a locally built static bundle. The Django/Render Python service must not load editor code from a third-party CDN at runtime.

## Why change the editor

The current editor converts Markdown to editable HTML and then serializes HTML back to Markdown. This is difficult to keep lossless for complex tables, nested content, custom figure references and future rich blocks. The existing Course Builder preview is also a large inline HTML/JavaScript file, so editor behaviour is difficult to isolate and test.

The new editor will use a structured ProseMirror document as the authoritative representation for migrated lessons. Markdown remains a supported import/export and compatibility format, not the canonical storage format.

## Existing data that must remain independent

The lesson body is not the entire lesson. The following current data contracts remain first-class and must not be flattened into rich text:

| Existing data | Current storage | Rebuild rule |
| --- | --- | --- |
| Lesson body | `Lesson.content_markdown` | Retain as legacy body and compatibility projection during migration |
| Lesson structured data | `Lesson.content_json` | Retain; add a versioned `lesson_document` member only after a lesson is migrated |
| Builder draft state | `CourseImport.payload.builder_state` | Retain draft IDs, module/lesson metadata and workflow state; add a versioned document alongside the existing lesson body |
| Practice questions (learner-safe) | `Lesson.content_json.questions` | Keep as a separate interaction model, with stable IDs and question-image references |
| Answer keys and rubrics | `LessonInstructorMaterial.rubric_json` | Keep instructor-only; never put correct answers or instructor notes in the learner document |
| Notebook and reflection | `Lesson.content_json.notebook/reflection` and learner progress | Keep as separate instructional/learner-response structures |
| Figures, image groups and comparison cards | `Lesson.content_json.figures` plus Markdown tokens | Use stable figure-reference nodes in the document; keep descriptive metadata in the existing sidecar until parity |
| Tables | Markdown plus `Lesson.content_json.tables` | Native table nodes with cell spans, alignment and widths; preserve legacy table metadata during transition |
| Regional lesson content and regional blocks | `Lesson.content_json.regional_lesson_content/regional_blocks` | Dedicated regional-reference nodes; keep variants and audience resolution outside generic prose |
| Images | `CourseMediaAsset` / `CourseImportAsset` and stable IDs | Store asset IDs, not data URLs or private storage paths, in document nodes |
| Protected videos | `ProtectedLessonVideo`, `CourseImportVideo`, personalised renditions | Reference opaque video/lesson IDs only; never store private source paths or stream keys in editor JSON |
| Lesson/course references | Stable lesson/course IDs | Dedicated reference nodes; preserve existing access checks |
| Publishing/review/pricing/catalogue | Existing CourseImport and Course models | Do not change these workflows as part of the editor rebuild |

The current editor/learner renderers remain available until the new renderer reaches feature parity.

## Canonical document envelope — version 1

Store the editor document under `lesson_document` in the existing JSON payload. Do not add a database column in the first migration stage.

```json
{
  "format": "tradethesis.lesson",
  "schema_version": 1,
  "content": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": [
          { "type": "text", "text": "A lesson paragraph." }
        ]
      }
    ]
  }
}
```

The envelope version belongs to TradeThesis. The nested `content` value is Tiptap/ProseMirror JSON.

The document body supports normal prose nodes and marks (paragraphs, headings, lists, blockquotes, code blocks, links, bold, italic, underline, strike and inline code), native table nodes, and TradeThesis reference nodes:

- `ttAssetImage`: references a managed asset by stable asset ID.
- `ttFigure`: references existing figure metadata by figure ID.
- `ttRegionalBlock`: references the existing regional-block sidecar by block ID.
- `ttLessonReference`: references a lesson by UUID.
- `ttProtectedVideo`: references the protected video record by opaque ID.

Questions, answer keys, notebook prompts, reflection responses, pricing, course metadata and publishing state are not generic document nodes.

Unknown nodes, marks, attributes, unsupported HTML and untrusted media URLs must produce a visible validation/import warning. They must never be silently dropped.

## Runtime and asset delivery

The Academy service runs on Render's Python native runtime. Tiptap therefore needs a build-time JavaScript toolchain, not a Node application runtime.

- Keep editor source and exact dependency pins under `backend/course_editor/`.
- Build a local browser bundle with Node in GitHub Actions.
- Commit the generated bundle to Django's static directory as a build artifact.
- Serve it through Django/WhiteNoise static storage. No CDN runtime dependency.
- Keep the new editor behind a disabled-by-default feature flag until parity tests pass.
- Continue using the current Course Builder page and save/review APIs during the first UI integration.

## Migration and compatibility rules

1. Existing lessons remain legacy Markdown and continue to open exactly as they do today.
2. Opening a legacy lesson is read-only with respect to migration. Merely opening it must not write or change its content hash.
3. Import legacy Markdown plus its sidecar JSON into a candidate Tiptap document. Record conversion warnings and unresolved references.
4. Compare a rendered preview and the original learner rendering. A candidate with unsupported content cannot be promoted.
5. On explicit save of a migrated lesson, write the versioned document and maintain the legacy Markdown projection/sidecar required by existing APIs.
6. Learner rendering moves to the document renderer only after server-side parity checks. Existing Markdown rendering remains the fallback for unmigrated lessons.
7. No bulk conversion or destructive migration. Migrate a small test course first; retain revision snapshots and an explicit rollback path.
8. Do not delete `content_markdown`, existing sidecar keys, old renderers or import compatibility code until all courses have been audited and the old path has no active readers.

## Delivery phases

### Phase 0 — contract and inventory
- Freeze the versioned document envelope and strict validator.
- Inventory every custom content token, sidecar and media interaction.
- Add schema tests and migration fixtures.
- No live editor switch and no saved-course writes.

### Phase 1 — editor package and isolated editor
- Add pinned Tiptap 3 packages and a deterministic build pipeline.
- Build an isolated editor module with the TradeThesis toolbar and custom reference nodes.
- Mount only in a development/QA surface; existing editor remains the default.

### Phase 2 — loss-aware legacy import
- Convert Markdown and existing sidecars to candidate document JSON.
- Produce a conversion report: converted, preserved as reference, warning, unsupported.
- Add fixtures from the real course packages, including Bollinger Bands and Support & Resistance.
- Never promote a document with unresolved content.

### Phase 3 — dual-write draft storage
- Keep the current builder state and legacy Markdown field.
- Save versioned JSON alongside it.
- Add conflict handling, autosave status and server-side schema validation.
- Preserve stable IDs and existing revision snapshots.

### Phase 4 — learner renderer parity
- Render the same structured document for editor preview and learner pages.
- Keep regional audience selection, asset authorization and protected video delivery server-side.
- Compare output for all supported block types and responsive layouts.

### Phase 5 — controlled pilot
- Enable the new editor only for a temporary QA course.
- Verify edit/save/reopen, learner preview, mobile layout, images, tables, regional content, questions and protected videos.
- Keep a feature-flag rollback to the existing editor.

### Phase 6 — gradual course migration and retirement
- Migrate approved courses in small batches with validation reports.
- Keep the Markdown import/export pathway.
- Remove old conversion code only after usage and regression evidence show it is unused.

## Feature-preservation acceptance checklist

- Typography: heading ladder, paragraph spacing, bold, italic, underline, strike, links, inline code and keyboard shortcuts.
- Lists: bullet, numbered, nested, task lists if currently used, start numbers and indentation.
- Quotes and code: blockquotes, language-labelled code blocks and long-fence-safe import/export.
- Tables: insert/delete rows and columns, cell selection, merge/split, row/column spans, alignment, widths, header groups, captions, mobile scrolling and the existing contextual delete interaction.
- Figures: single figures, captions, alt text, multi-image groups, comparison cards, figure order and exact IDs/placement.
- Regional content: country and regional variants, hidden states, media references and audience-specific fallback.
- Practice: question order, option order, image references, correct answer and explanation in instructor-only storage, learner-safe payload.
- Notebook/reflection: prompts, labels, lesson-specific defaults and learner response persistence.
- Video: existing upload/processing state, protected HLS, personalised watermarking and authorization.
- References: lesson cards and related-course references.
- Workflow: draft save/reopen, rejected draft editing, published-course revision, review, approval, publication and pricing remain unchanged.
- Safety: sanitisation, CSRF, role permissions, protected assets, no private video URLs in JSON, and invalid-content warnings.
- Responsive behaviour: desktop and mobile editing, sticky contextual toolbar, no horizontal page overflow.

## Explicit non-goals for the first release

- No collaborative real-time editing.
- No comments, track changes, AI writing features or cloud conversion services.
- No rewrite of the course catalogue, pricing, entitlements, learner progress, protected video system or admin review desk.
- No automatic bulk migration.
- No production deployment until the staging pilot passes.
