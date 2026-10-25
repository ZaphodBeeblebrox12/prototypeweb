# Sitewide instructional-image replacement

Status: The standalone learning-room preview exposes a local-only image replacement control. Production replacement remains a Django backend task; server upload is enabled only by authenticated server-rendered configuration.

## Intended experience

An authorised administrator opens a lesson, selects Replace image beside a figure, uploads a JPG, PNG or WebP, and receives a clear success/error message. The update applies to every displayed use of the same stable asset, and learners then receive the newest shared image. Students and ordinary learners do not see editing controls.

Shared frontend assets:
- site/assets/instructional-image-admin.js
- site/assets/instructional-image-admin.css

They are included in the Trading Path and Support & Resistance learning-room templates. The standalone preview uses a labelled local image chooser for layout testing; it only changes the open preview session. It does not upload or persist media. Production controls must be gated by Django permissions, never a query parameter or client-side role flag.

## Server contract

Only a server-rendered template that has checked the user's staff and media-edit permission should emit configuration similar to this:

    window.TRADETHESIS_MEDIA_EDITOR = {
      enabled: true,
      csrfToken: "SERVER_RENDERED_CSRF_TOKEN",
      maxBytes: 10485760
    };

Each editable image must include stable metadata supplied by the backend: data-media-asset-id and data-media-replace-url. The sample URLs or IDs are not live routes. Never activate the control from a query parameter, local storage or a client-side role flag. The upload endpoint must re-check permission for every request.

The frontend sends multipart POST fields image and asset_id plus X-CSRFToken. A successful endpoint returns JSON with ok=true, image_url and optional alt. Every rendered use of the same asset ID on the current page is updated to the returned, cache-safe URL.

## Backend work still required

The current prototypeweb repository is static and does not contain the Django runtime. Its separate Academy app stores lesson text and learner-safe JSON but does not currently have a shared instructional-media model or image-replacement endpoint. Persistent replacement requires a backend pass in the deployed Academy app after its target branch and release are agreed. Keep the change small rather than creating a general media-management platform.

Backend acceptance requirements:
1. Add a shared media record with stable ID, persistent image storage, alt text, course/lesson association as needed, and who/when audit fields.
2. Render the same media record in every use with stable ID and authorised replacement URL.
3. Use a CSRF-protected POST endpoint restricted to authenticated administrators with a dedicated media-edit permission assigned only to administrators. The hidden button is not security.
4. Validate the decoded image server-side; allow JPEG/PNG/WebP, enforce file-size limits and safe generated filenames. Do not accept SVG uploads as user content.
5. Store to persistent shared storage and return a versioned/cache-safe URL only after the storage and database update succeed.
6. Keep the old file available for recovery until the new image is verified.
7. Test staff success; learner/anonymous denial; CSRF failures; unsupported/oversized files; storage failure; repeated use of one asset; and the learner view after replacement.

Release boundary: shared upload is not production-ready until backend storage, permissions, records, endpoint and acceptance tests exist. The local preview flag is not authentication and must not ship as a production editing gate.