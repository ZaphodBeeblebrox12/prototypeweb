# Academy integration working branch

**Product/content source of truth:** `ZaphodBeeblebrox12/prototypeweb`  
**Working branch:** `feature/tradethesis-academy`  
**Only merge target:** `my-new-branch`  
**Forbidden merge target:** `main`

## Working rules

- Keep all future Academy integration changes on this repository's `feature/tradethesis-academy` branch.
- Open the draft pull request against `my-new-branch` only after the branch contains real integration work.
- The PR's base must remain `my-new-branch`; never retarget it to `main`.
- Preserve the existing static TradeThesis site, course-room previews, micro-course source, and course assets already on the base branch.
- The previous draft PR in `ZaphodBeeblebrox12/test` was closed because its base was `main` in a separate repository. Its source branch remains available for reference; it was not merged.
- Do not claim the Django runtime has been copied, deployed, or connected until the actual files and routes are in this repository and runtime validation is recorded.

## Integration objective

Bring the authenticated Academy experience into the current product branch without losing the existing catalogue and micro-courses. Map course source manifests to backend records, preserve a distinct offer/entitlement policy for each course, keep progress/payment confirmation server-side, and maintain the light TradeThesis visual system across public pages, member area, learner room, checkout and course administration.

Course development is ongoing. New courses must be possible without redesigning the catalogue. The friendly admin dashboard remains a later milestone, after core learner-facing journeys and access/persistence flows are connected and tested. Sitewide UX remains a continuous review item.
