# Bollinger Bands — Academy staging and release gate

**Branch:** `my-new-branch`  
**Course slug:** `understand-bollinger-bands`  
**Source of truth:** Existing course manifest and authored Markdown. Lesson copy is unchanged by this work.

## Stage for administrator review

After the Academy backend branch is available in the intended staging environment, run from the repository root:

```bash
cd backend
python manage.py import_microcourse --manifest ../course-source/understand-bollinger-bands/course-manifest.json --dry-run
python manage.py import_microcourse --manifest ../course-source/understand-bollinger-bands/course-manifest.json
```

The second command creates or reuses a review-only import snapshot. It does not publish Course/Module/Lesson rows, create a CourseOffer, enable checkout, grant entitlements or deploy the site. Review it in **Django Admin → Academy → Course imports → Review**.

## Before publication

- [ ] Visually inspect all 30 authored SVG figures in the canonical Learning Room at desktop and mobile widths and 200% zoom.
- [ ] Replace all 32 temporary Module 5 remote historical-chart references with approved local TradingView captures or rights-cleared local images. Academy validation blocks these Bollinger-specific remote references until a local replacement is uploaded.
- [ ] Review all seven modules and 30 lessons, including answers, captions, readability, mobile layout and source attribution.
- [ ] Confirm persistent shared media storage is configured.
- [ ] Publish only through the administrator approval flow after validation passes.
- [ ] Create and activate the dedicated one-time CourseOffer separately; importing/publishing content does not set price or checkout access.

Admin uploads remain restricted to decoded JPEG, PNG or WebP. Checked-in course-source SVGs are accepted only through a strict static-SVG validator; script, external-resource, link, style and unknown SVG elements/attributes are rejected.

## Execution note

The connected Render tools cannot run Django management commands, and the read-only database connector was blocked because the database has an empty IP allowlist. This document prepares the exact steps; it does not claim the Academy import has already been staged.
