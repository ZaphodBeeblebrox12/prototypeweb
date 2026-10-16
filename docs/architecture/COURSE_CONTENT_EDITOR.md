# Course lesson text editing — Django handoff

Status: The static Bollinger learning-room preview has a browser-local editing prototype. Shared saves are not connected yet.

## Intended staff experience

An authorised staff member opens a lesson, selects **Edit lesson text & images**, edits student-facing text in place, and selects **Save text draft**. Once wired to Django, the same content should be shared by staff and learners. Browser-local draft saving is only for testing the interaction.

## Frontend contract

The preview sends `course_id` and a list of `fields`, each with `content_id` and updated `html`. Example configuration for a Django template after checking staff permission:

```js
window.TRADETHESIS_CONTENT_EDITOR = {
  enabled: true,
  csrfToken: "SERVER_RENDERED_CSRF_TOKEN",
  saveUrl: "/staff/course-content/save/"
};
```

The URL is a contract example, not an implemented route. The endpoint should return JSON `{"ok": true}` only after its database transaction succeeds.

## Minimum backend acceptance

1. Persist content using the existing course/Academy content model; do not build a general-purpose page builder.
2. Render controls only for authenticated staff with course-content edit permission. Re-check permission on each POST.
3. Require CSRF protection.
4. Render stable content IDs from persisted lesson fields/blocks. Do not use the preview's tag-order-generated IDs as the permanent schema.
5. Validate fields and sanitise HTML against scripts, event handlers, iframes, unsafe URLs and other active content.
6. Save changes transactionally and retain a simple previous-value/revision record with editor and timestamp.
7. Test staff save, learner and anonymous denial, CSRF failure, invalid markup/payload, database failure and the learner view after saving.

The first scope is lesson headings, explanations, figure captions and practice/question text. Layout, figure numbering, media IDs, navigation labels, progress state and interactive logic remain controlled by code.
