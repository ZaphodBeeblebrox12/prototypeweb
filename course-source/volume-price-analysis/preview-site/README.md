# VPA standalone preview

This folder is the isolated learner-facing website for **Read Volume. Find Trade Setups.** It lives next to the editable course manuscripts and production assets, so teaching content and presentation can be developed in parallel.

## Open the preview

Open `index.html` in a current browser. It is a self-contained HTML file: styles, lesson navigation, practice-stage interactions and the illustrative chart are embedded, so the preview does not need a build step or a package install.

For a local server from the repository root, run:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/course-source/volume-price-analysis/preview-site/`.

## What this preview contains

- Navigable curriculum for all six modules and 30 lessons.
- Search across lesson titles.
- Learner-facing lesson objective, teaching rhythm and module-level takeaway.
- A small interactive practice frame with Notice, Compare, Apply and Review stages.
- Direct links to each module manuscript and to the existing M01-L01 pilot ChartLab.

The preview is deliberately independent of `site/`. Nothing here has been added to the public course catalogue, and no checkout, enrolment or server-side learner progress is connected.

## Source map

- `../lessons/` — lesson manuscripts and editorial/teaching notes.
- `../assets/` — production brief, pilot ChartLab, charts, data and accessibility notes.
- `course-manifest.json` — course/module/lesson metadata and production status for later integration.
- `PRODUCTION_NOTES.md` — current scope and remaining verification.

## Important boundaries

This is a course-design preview, not a finished, access-controlled delivery system. Do not publish the entire `course-source/` tree to a public web server: it contains paid-course material and internal production documents. Any production integration must expose only approved learner-facing content behind the intended access controls.

The four-stage rhythm promises practice and review. As more lesson-specific activities are built, make sure published lessons actually deliver those activities and feedback rather than relying on the layout alone.
