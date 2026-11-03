# Academy Course Builder: maintenance boundaries

## Canonical ownership

| Concern | Canonical owner | Maintenance rule |
|---|---|---|
| Authoring controls, editable lesson canvas, draft state and editor interactions | `apps/academy/course_builder_preview.html` | Avoid adding another global event handler or wrapping a renderer/action handler without documenting the order. |
| Lesson markers, structured image tokens, group tokens, quote/tab routing and safe Markdown rendering | `apps/academy/content_rendering.py` | Keep learner-visible output canonical here. Compatibility code may translate old authored markup, but must emit current component markup. |
| Learner-room component layout and local interaction styling | `static/academy/learning-room.css` | Do not duplicate shared typography or approved content-component systems here. |
| Shared Builder/learner typography, quote treatment, table treatment and Hard-block Index presentation | `static/academy/course-template-parity.css` | This file is loaded after the learner component CSS and after the Builder's embedded styles. Put shared approved design rules here once. |
| Rendering and styling regressions | `apps/academy/test_content_rendering.py` and related Academy tests | Add assertions at the shared rendering boundary; avoid tests that only assert the presence of a CSS string when output behavior can be asserted. |

## Approved instructional image system

The Hard-block Index is the single approved presentation for both standalone chart images and multi-image groups.

- The renderer emits `tt-image-group-hard-index` for a one-image block and for a grouped block.
- The Hard-block Index CSS has one source of truth in `course-template-parity.css`.
- Generic `tt-purpose-figure` card rules must exclude `.tt-image-group-hard-index`; they remain available for other purpose-built figure types.
- Uploaded image assets, lesson references and image-group membership are separate concepts. Removing a lesson reference must not delete the uploaded asset or other references.

Legacy authored image markup may remain supported through a narrow compatibility adapter in `content_rendering.py`. That adapter must emit the current Hard-block Index markup, not revive a retired visual template.

## Quotes and section routing

Design 07 (Context First) is shared by the learner view, Builder preview and editable canvas through `course-template-parity.css`.

The `[[lesson-tab:...]]` markers are authoring metadata, not learner content. A marker serialized inside a Markdown blockquote must be removed as metadata without changing the quote or routing the next heading. Keep server-side parsing and Builder preview handling aligned.

## Known refactor work not included in this styling cleanup

The Builder HTML remains a large integrated authoring surface. Its script currently extends some core functions in layers (notably `renderMarkdown`, `renderEditor` and `handleAction`) and uses several delegated document listeners. Those layers are order-dependent today.

Do not casually remove a wrapper or consolidate listeners as a cosmetic cleanup. The next safe architectural phase is to:

1. introduce an explicit action-handler registry and render extension hooks;
2. move editor logic into small static modules while keeping one state owner;
3. move the remaining embedded Builder component styles into owned stylesheets;
4. add browser-level tests for insertion, drag/reorder, removal, save/reopen, audience switching, undo/redo and learner-preview parity;
5. remove compatibility paths only after existing saved drafts have been covered by migration or fixture tests.

Each phase should be independently reviewable and should preserve the approved Hard-block Index, Design 07 quote, Alternating Field Notes tables and learner-facing typography.

## Verification

Run focused renderer tests from `backend/`:

```bash
pytest apps/academy/test_content_rendering.py -q
```

The repository's `verify-django-backend.yml` workflow runs the broader Academy regression suite on pushes to `my-new-branch` and on pull requests targeting that branch. Do not treat a successful Render build or health check as a substitute for the test suite.
