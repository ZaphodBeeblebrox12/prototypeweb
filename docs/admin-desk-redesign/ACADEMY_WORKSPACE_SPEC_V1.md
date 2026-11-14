# TradeThesis Admin Desk — Academy Workspace Specification V1

**Status:** First screen-level design proposal; owner review pending  
**Date:** 2026-11-14  
**Planning branch:** `admin-desk-redesign-planning`  
**Source baseline:** `my-new-branch`  
**Visual template:** Approved V2 forest-green / warm-ivory shell, restrained terracotta and sage, editorial serif page headings, compact sans-serif controls.  
**Implementation status:** Planning and static mockup only. No application code, routes, permissions, APIs, database records or deployment settings have been changed.

## 1. Scope and design intent

This specification develops the Academy domain into a set of connected staff workspaces:

1. Academy Overview (M03)
2. Course Catalogue (M04)
3. Course Detail / Control Page (M05)
4. Course Approvals Queue (M06)
5. Course Review Detail (M07)
6. Course Builder hand-off (M26)
7. Offers & Access (M08)
8. Learner Access & Progress (M09)
9. SEO & Discoverability (M25)

The intent is not to put every Academy action on one screen. Each destination should do one job well, and the same underlying record must be opened from its canonical owner. Academy owns course content, course publication workflow, CourseOffer and direct course entitlements. Revenue owns Plan and price records. Customers owns learner accounts and Customer 360. Platform owns durable job and external provisioning details.

All records, names, counts, prices, dates and learner activity in the clickable prototype are fictional. Interactions only change the static prototype view or show explanatory messages.

## 2. Source-verified Academy model

### 2.1 Course

The current Course model has three separate classification dimensions:

**Publication status**
- Draft
- Published
- Archived

**Catalogue role**
- Flagship programme
- Supporting programme
- Mini-course
- Hidden (not listed on the Courses page)

**Access type**
- Free course
- Included in free membership
- Paid individual purchase
- Free membership or individual purchase (Mixed)

These dimensions must never be collapsed into one generic status. For example, a course can be published, marked as a Mini-course and have Mixed access.

Other relevant fields include title, slug, summary, description, SEO title, SEO description, primary topic, course-level indexability flag, category, level, estimated duration, learning outcomes and display position.

### 2.2 Curriculum

CourseModule belongs to Course and has title, slug, description, position and publication state.

Lesson belongs to CourseModule and has title, slug, summary, format, content payload, position, duration, preview flag, publication flag and release_day. Lesson formats include Reading, Video, Interactive and Quiz.

Lesson progress is stored separately in LessonProgress, linked to a user and lesson. Progress statuses are Not started, In progress and Completed. The model records started/completed/last-seen timestamps and time spent. Learner responses are kept separate from instructor-only answer keys and rubrics, which live in LessonInstructorMaterial.

### 2.3 CourseImport and editorial workflow

CourseImport is the persisted Course Builder draft/submission record. Its status values are:

- DRAFT — Builder draft
- REVIEW — Awaiting review
- PUBLISHED — Published
- REJECTED — Returned/rejected
- SUPERSEDED — Superseded by a newer import
- DELETED — Deleted by an administrator

CourseImport also records course_slug, title, manifest version, content hash, source manifest, JSON payload, optional target_course, imported_by, reviewed_by, imported_at, updated_at and published_at.

A submission with target_course is a revision of an existing course. It must be shown differently from a new course submission. The review page explicitly tells the reviewer that a revision does not mutate the live Course while it is under review; publication updates the existing course while preserving its identity and matching lesson records.

The queue queryset is ordered newest submission first by imported_at. The prototype uses that order.

### 2.4 CourseOffer and Revenue relationship

CourseOffer belongs to Academy and has:
- Course
- Name and slug
- One-to-one linked commerce Plan (optional while being configured)
- access_duration_days (blank/NULL means permanent access)
- active state and display position

The current model validation for an active offer requires:
- A linked Plan.
- The course must be Published.
- The course access type must be Paid or Mixed.
- The linked Plan must be hidden from the public subscription catalogue.
- An active one-time PlanPrice or GeoPlanPrice must exist.

A Plan with PaymentIntent or Subscription history cannot simply be reused for a new CourseOffer. Once a payment intent exists, the existing offer's course, plan and access duration are constrained; future changes may require a new offer rather than rewriting the purchase history.

**Ownership boundary:** Academy owns CourseOffer and its relationship to a Course. Revenue owns Plan, PlanPrice and GeoPlanPrice. Do not duplicate a price editor inside Academy. Show the linked Revenue Plan and price context and open the canonical Revenue record for commercial configuration.

### 2.5 Learner access paths

The learner-access UI must distinguish at least these paths:

**Direct CourseEntitlement**
- Links User and Course.
- May also link CourseOffer and PaymentIntent.
- Source is Purchase, Administrator grant, Migration or Complimentary.
- Stored status is Active or Revoked.
- Starts_at and expires_at determine whether access is currently valid.
- Revoked state and expired-by-date state are different.
- A future starts_at can be presented as Scheduled even while stored status remains Active.
- A blank expiry means permanent access.
- CourseEntitlement is unique for a given user/course pair.

CourseEntitlementEvent records Granted, Extended, Reinstated and Revoked, with actor, reason, details, optional payment link and timestamp.

**Free-course enrolment**
- The current enrolment service creates a permanent CourseEntitlement with Complimentary source for a Published course whose access type is Free.
- The service writes the corresponding entitlement event.
- It is not a paid CourseOffer purchase.

**Free membership inclusion**
- PlanCourseAccess maps a Plan to a Course.
- The inspected current service path specifically resolves the dedicated TradeThesis Free product/Free tier, non-trial, active, public, zero-price monthly Plan and active PlanCourseAccess mapping.
- The current helper does not establish that every subscription tier automatically unlocks mapped courses. Do not show Pro/paid-plan course inclusion as live capability unless a separate source audit proves that path.
- Membership access is not a second direct CourseEntitlement purchase record.

**Direct paid-course purchase**
- The payment confirmation path verifies the provider state.
- activate_paid_subscription detects that the Plan belongs to a CourseOffer and dispatches to apps.academy.services.activate_course_payment.
- activate_course_payment atomically claims the PaymentIntent and grants/links the CourseEntitlement with Purchase source and payment reference.
- Newly created entitlements can trigger personalised-video jobs and an Academy domain event; non-simulated receipt notification runs after commit.

Payment state, application access and external provisioning must remain separate states.

### 2.6 Permissions

The shared course-content policy is not generic staff access:
- Superusers are allowed.
- An authenticated user whose role is explicitly `admin` is allowed.
- Ordinary `is_staff` alone is not sufficient.

The existing Course Builder preview, review queue/detail/actions and SEO dashboard use this course-content permission check.

Customer 360's Academy panel uses separate model permissions: the inspected view requires both Academy CourseEntitlement view permission and LessonProgress view permission before presenting the Academy records. A full role/group permission matrix is still required before the new shell's role-specific visibility is frozen.

## 3. M03 — Academy Overview

**Purpose:** Help the Academy operator answer: what needs editorial or learning-product attention now?

**Primary user:** Course-content administrator / Academy operator.

### Layout order

1. Page identity and shared V2 shell.
2. Four compact context indicators:
   - Courses in catalogue.
   - Submissions awaiting review.
   - Active/saleable CourseOffers.
   - SEO pages needing attention.
3. Main attention queue:
   - Course submissions awaiting review.
   - Published course with a concrete metadata/indexability blocker.
   - Offers that fail saleability checks.
   - Learner access exceptions only when an underlying record/query supports them.
4. Secondary course lifecycle explainer.
5. Compact catalogue-role snapshot.
6. Cross-domain relationship strip:
   - Revenue for Plan/price.
   - Customers for learner record/progress.
   - Platform for job/provisioning state.

### Behaviour

- Every attention item must deep-link to the domain/page that owns its resolution.
- Counts must come from real records, permission-scoped queries and defined filters before implementation. Mockup counts are not a target or a verified live count.
- Metrics remain secondary to actionable work.
- The page must not report an access exception merely because a job is pending; the access model and job model are distinct.
- A course can be published while its offer is not saleable or SEO is blocked. Keep those states separate.

### Existing foundation and proposed work

The current `/staff/admin-desk/` view already computes course counts, import review counts, active offer counts, active entitlement counts and lesson progress counts for authorised course-content administrators. The proposed M03 is the unified Academy home and should reuse the canonical queries/services where appropriate rather than creating new ledgers or duplicating calculations.

## 4. M04 — Course Catalogue

**Purpose:** One compact, filterable register of Course records.

### Recommended columns

- Course title and slug.
- Catalogue role.
- Publication status.
- Access type.
- Module/lesson publication context.
- CourseOffer state: none, inactive, active/saleable or needs attention.
- SEO/indexability status.
- Last updated.
- Action to open Course Detail.

### Filters and search

- Search title or slug.
- Catalogue role: Flagship, Supporting, Mini-course, Hidden.
- Publication: Draft, Published, Archived.
- Access type: Free, Membership, Paid, Mixed.
- Offer state.
- SEO/indexability and attention state.

### Interaction rules

- Use a dense table, not large marketing cards.
- The first click opens the canonical Course Detail, not a duplicate course record.
- “Open in Builder” is an authoring hand-off, not a publication action.
- Offer and SEO indicators are contextual read summaries; their controls belong in the relevant destination.
- Empty states must distinguish no courses from no results for the selected filters.
- Keep the row readable at 1280–1440px and allow horizontal scroll at narrow widths without forcing the entire page to overflow.

### Existing foundation

Course model and related models exist. The inspected source map does not show a dedicated staff-facing Course Catalogue page inside Admin Desk; some record administration remains in Django Admin and the public catalogue API is not a staff administration screen. M04 is a proposed unified page.

## 5. M05 — Course Detail / Control Page

**Purpose:** One canonical Course record with clear internal sections and linked records.

### Record header

- Title and slug.
- Catalogue role.
- Publication status.
- Access type.
- Updated timestamp.
- Course identity.
- Actions: open Builder, return to catalogue; publishing actions must not appear here as a shortcut around approvals.

### Internal sections

**Overview**
- Identity and summary.
- Publication and content readiness.
- Separate discoverability, saleability and learner-access state.
- Recent course lifecycle activity where supported.

**Curriculum**
- Module/lesson outline and positions.
- Publication state.
- Lesson format and duration.
- Release day / preview where relevant.
- Do not edit lesson bodies inside the catalogue control page. Open the existing Builder.

**Catalogue & SEO**
- Public title/summary/description and catalogue role.
- SEO title and description.
- Primary topic.
- seo_indexable flag.
- Actual reasons for indexability/blocking.
- Deep link to SEO inventory.

**Offers & Membership**
- CourseOffer(s) for individual purchase.
- Linked hidden Revenue Plan and price reference.
- Access duration.
- Current saleability reasons.
- Membership inclusion shown only when a source-backed PlanCourseAccess relationship is present; the current free-membership path should be labelled clearly.

**Learner Activity**
- Direct CourseEntitlement summaries and event history.
- Progress based on published lessons and LessonProgress.
- Membership-plan access summary separately labelled.
- Open the learner/customer record in Customers for the full customer history.

### Cross-domain context

- Revenue: canonical Plan, PlanPrice, GeoPlanPrice, PaymentIntent, Refund, Invoice.
- Customers: canonical learner account and Customer 360.
- Growth: referral/discount provenance only where the source relation supports it.
- Platform: protected-video processing jobs or other linked operations when the source record exists.

### Hard boundary

Course Detail is the control/overview page for the Course record. It is not a replacement for the Builder, approval workflow, Revenue plan editor or Customer 360.

## 6. M06 — Course Approvals Queue

**Purpose:** Show CourseImport submissions that require editorial decisions.

### Queue columns

- Submission title and slug.
- New course vs revision.
- Target Course for revisions.
- Author/imported_by.
- Imported/submitted time.
- Manifest version.
- Asset readiness summary.
- Publication validation summary.
- Action to open Review Detail.

### Queue semantics

- Default queue is CourseImport status REVIEW.
- Sort newest submission first, matching the current model ordering/query.
- Show revision identity prominently. Never treat a revision as a separate new public Course.
- Returned/rejected submissions are not active review queue items, but may be discovered through the Builder lifecycle/history.
- Superseded and deleted records should not appear in the normal waiting-for-review queue.
- Counts must be permission-scoped.

### Existing route

`/staff/admin-desk/courses/review/` is the existing Admin Desk queue. It checks the course-content-admin policy and queries CourseImport status REVIEW. M06 is a visual and navigation redesign of this existing queue, not a new workflow.

## 7. M07 — Course Review Detail

**Purpose:** Allow an authorised reviewer to inspect one exact staged submission and make a controlled decision.

### Page layout

**Header**
- Submission title.
- CourseImport status.
- New vs revision.
- Author.
- Course slug.
- Manifest version.
- Submitted time.
- Existing target Course identity for revisions.

**Main review area**
- Learner-safe staged curriculum preview.
- Module and lesson accordions.
- Video links/previews where valid.
- Figures/images and alt text.
- Staged asset availability, external source and replacement state.
- Publication validation errors.

**Reviewer rail**
- Validation checklist.
- Approve and publish control only when canonical validation passes.
- Return-to-editor control with mandatory reviewer feedback (up to 2,000 characters in the current route).
- Clear visibility of who is reviewing the submission.

### Existing business rules to preserve

- Approve is a POST to the existing canonical publisher `publish_course_import`; it must not write partial course records via a new UI-specific code path.
- Return requires non-empty reviewer feedback. The existing view records feedback in the payload, sets CourseImport status REJECTED, stores reviewed_by and writes an audit event.
- A revision leaves the current live Course unchanged while awaiting review.
- The private review asset endpoint is read-only in the Admin Desk review page; the existing shared review context can show asset state/source.
- Permanent test-import cleanup is separate. It is only enabled for eligible unlinked/unpublished imports with no matching Course; it requires typing DELETE and removes staged files after commit. Do not place a casual Delete button beside Approve/Return.
- The screen is restricted to authorised course-content administrators.

### Empty and error states

- No reviewable submissions.
- Missing private asset.
- External image URL cannot be previewed.
- Validation failure prevents approval.
- Permission denied.
- Publication service validation error; show the validation feedback and preserve the staged submission.

## 8. M26 — Course Builder hand-off

**Purpose:** Provide a clear route from the Admin Desk into the current authoring environment while preserving the lifecycle boundary.

### Existing destination

- Main Builder route: `/staff/course-builder/`.
- Builder API: `/staff/course-builder/api/`.
- Associated video/asset endpoints and Google Drive OAuth routes exist.
- The Builder preview is protected by the course-content-admin permission.
- Builder drafts are persisted as reviewable CourseImport records.
- Submitting for review does not publish the live Course.
- Publication remains a separate reviewer action.

### Proposed launchpad behaviour

- Search/select a course or saved Builder draft.
- Continue a draft or start a new authoring draft through the existing Builder.
- Show draft/review/returned/published lifecycle context.
- Preserve selected course/import context and a clear return path to Academy.
- If the submission has been returned with feedback, surface that reviewer feedback in the hand-off summary.
- Keep media/figure upload and lesson-body editing inside the existing Builder.

### Tiptap boundary

A separate staff Tiptap preview/API route exists under `/staff/course-builder/tiptap/`. It is a development/feature-gated path and is not treated as the production/default editor in this redesign. The selected design must preserve the existing supported Builder until Tiptap has separately passed persistence, preview, validation, authoring parity and release gates.

## 9. M08 — Offers & Access

**Purpose:** Coordinate individual course offers and course access rules while preserving Revenue as the owner of commercial Plan and price records.

### CourseOffer register

Recommended columns:
- Course / offer.
- Course publication status.
- Course access type.
- Linked commerce Plan (hidden status).
- One-time price configuration status.
- Access duration.
- Offer active state.
- Derived saleability and exact reason.

### Offer detail / editor structure

**Academy-owned section**
- Linked Course.
- Offer name/slug.
- Active/inactive state.
- Access duration: permanent if blank, or a defined number of days.
- Current validation state.

**Revenue-owned linked record**
- Plan name and hidden status.
- Product/tier/active state, where permitted.
- Active one-time global and/or geo price rows.
- Link to Revenue for price edits.

### Safety and validation

- An active offer requires a Plan.
- Course must be Published.
- Course access type must be Paid or Mixed.
- Plan must be hidden.
- At least one active one-time PlanPrice or GeoPlanPrice is required.
- Reusing a Plan with payment/subscription history for a new course offer is blocked.
- If an existing offer has PaymentIntent history, changing Course, Plan or access duration is constrained. Future sales changes may require a new offer.
- Do not reinterpret an old payment as a purchase of a different course or a different access term.

### Status model

Do not present a single editable “saleable” checkbox. Show the stored active flag and the derived saleability conditions separately. A record can be Active but not currently saleable because the linked course, plan or price requirement fails.

## 10. M09 — Learner Access & Progress

**Purpose:** Inspect which learners can access which course and what progress they have made, without conflating distinct access paths.

### Internal sections

**Direct course entitlements**
- Learner and course.
- Source: Purchase, Administrator grant, Migration or Complimentary.
- Stored entitlement status: Active / Revoked.
- Start and expiry.
- Derived state: Active, Scheduled, Expired or Revoked.
- Linked CourseOffer and PaymentIntent where present.
- Grant actor and revocation reason where permitted.

**Membership inclusion**
- PlanCourseAccess record and linked Plan.
- Show active Subscription evidence separately.
- The current service-verified path specifically checks the dedicated TradeThesis Free plan/product and its active zero-price monthly configuration. Do not assume every membership tier grants access through this service.

**Learner progress**
- Course and module/lesson completion.
- Completed lesson count / total published lesson count.
- Last activity and time spent.
- Link to Customer 360.
- Do not show instructor answer keys/rubrics or private internal material in the learner progress screen.

**Entitlement events**
- Granted, Extended, Reinstated, Revoked.
- When, actor, reason, linked payment if applicable.

### Actions

Any future Grant, Extend, Reinstate or Revoke action must use the established Academy entitlement service, check the relevant staff permission, require an appropriate reason, and write CourseEntitlementEvent/audit history. No such write action is implemented by this prototype. Do not use a direct database edit or a parallel entitlement table.

### Permission boundary

The current Customer 360 view requires both Academy CourseEntitlement view permission and LessonProgress view permission to display the Academy panel. The full standalone Academy learner-access screen requires a dedicated role/permission audit before visibility and actions are specified.

## 11. M25 — SEO & Discoverability

**Purpose:** Diagnose whether public course overview pages meet the current technical/editorial indexability checks.

### Summary/context

- Site-wide indexing enabled/disabled.
- Published course count.
- Eligible-for-indexing count.
- Published but blocked count.
- Pages requiring editorial attention.
- Missing descriptions and primary topics.
- Distinct/shared primary topics.

### Per-course table

- Course and slug.
- Effective search title and whether it is custom/fallback.
- Effective description and whether it is custom/course-copy/missing.
- Indexability result.
- Exact blocking reasons.
- Editorial issue labels.
- Deep link to course/Builder.

### Current source checks

The existing SEO dashboard considers:
- Global `TRADETHESIS_SEO_INDEXABLE` setting.
- Course is Published.
- Course `seo_indexable` flag.
- Course is not Hidden from the public catalogue.
- At least one published lesson.
- Public catalogue content checks (title/summary/description recommendation rule).
- Search title/description fallback and length guidance.
- Missing primary topic.
- Duplicate effective search titles.
- Repeated primary topics.

Shared primary topics are an editorial prompt to check whether pages answer distinct learner questions. They are not proof of a search penalty or a prediction of ranking outcomes.

### Existing route

`/staff/admin-desk/seo/` is an existing permission-protected SEO inventory. M25 should preserve its diagnostic meaning and link into the Course Detail and Builder, not add unsupported keyword-volume or Google-ranking metrics.

## 12. End-to-end Academy journeys

### Journey A — New course to publication

Builder draft → CourseImport REVIEW → Approval Queue → Review Detail → canonical validation → approve/publish → Course record becomes available for catalogue/SEO checks.

### Journey B — Revision of an existing course

Builder creates a revision linked to target_course → revision enters review while current live Course remains unchanged → reviewer compares the staged version → return with mandatory feedback or approve exact revision → canonical publisher updates the existing Course identity and matching lesson records.

### Journey C — Published course to individual sale

Published Course with Paid/Mixed access → CourseOffer → dedicated hidden Revenue Plan → active one-time PlanPrice/GeoPlanPrice → saleability checks pass → provider-verified PaymentIntent → atomic Academy entitlement grant → direct CourseEntitlement → learner progress.

### Journey D — Free course enrolment

Published Course with Free access → learner enrolment → complimentary direct CourseEntitlement → entitlement event → learner progress.

### Journey E — Free membership course inclusion

Course marked Membership/Mixed → course publication synchronises dedicated TradeThesis Free PlanCourseAccess mapping → learner with a qualifying active TradeThesis Free subscription can access the mapped course according to the current access/release service.

### Journey F — Learner support/access investigation

Support ticket → Customer 360 → Academy learner access/progress summary → direct entitlement, membership inclusion or progress detail → canonical Revenue/Platform record where the issue crosses domains.

## 13. Prototype artefact and review status

**Clickable prototype:** `tradethesis_admin_academy_workspace_v1.html`

It includes:
- Academy overview and attention queue.
- Course Catalogue with search and filters.
- Course Detail with internal tabs for Overview, Curriculum, Catalogue & SEO, Offers & Membership, Learner Activity.
- Course Approvals Queue.
- Review Detail with revision, assets, validation and reviewer decision.
- Course Builder hand-off.
- Offers & Access register and model rule explanation.
- Learner Access & Progress with Direct Entitlements, Membership Inclusion, Progress and Entitlement Events.
- SEO & Discoverability diagnostics.
- Six-domain V2 shell and cross-domain hand-off explanations.

**Browser smoke tests performed**
- Catalogue search/filter.
- Open Course Detail and internal tab navigation.
- Course Approval → Review Detail navigation.
- Offers & Access navigation.
- Learner Access internal tabs.
- SEO navigation.
- Mobile menu opens, navigates and closes.
- No JavaScript page errors observed in the exercised flows.
- Mobile viewport test at 390px showed no horizontal page overflow.

**Not tested / not claimed**
- Accessibility/keyboard and screen-reader audit.
- Measured contrast certification.
- Authenticated live staging visual parity.
- Actual source API data and live role-specific visibility.
- Real save, publish, grant, revoke, price edit, refund or operational actions.
- Complete mobile/tablet design beyond the smoke-tested mobile viewport.

## 14. Review decisions requested

1. Is the Academy landing page's attention-first hierarchy right?
2. Is the Course Catalogue table the correct density and set of columns?
3. Does Course Detail provide the right internal tabs, or should any section become a separate top-level destination?
4. Does the review queue/detail preserve the importance of new vs revision and the staged-vs-live distinction?
5. Is the Builder hand-off clear enough that authoring and publishing remain separate?
6. Is the CourseOffer / hidden Plan / Revenue price split understandable?
7. Is the separation between direct entitlement, free membership inclusion and progress sufficiently clear?
8. Does the SEO screen communicate technical eligibility without suggesting ranking guarantees?
9. Which Academy screen needs the next high-fidelity pass before we move to Customers?

This specification is a design proposal. It does not authorise implementation.
