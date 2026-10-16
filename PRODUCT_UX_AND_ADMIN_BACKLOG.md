# Product & UX Backlog — Admin Dashboard and Sitewide Experience

**Repository/branch:** `ZaphodBeeblebrox12/prototypeweb` / `my-new-branch`  
**Purpose:** Durable product note for implementation planning. Preserve existing course, micro-course, and learning-room work; do not treat these notes as permission to rewrite already-approved content without review.

## Confirmed priorities from the product owner

### 1. Sitewide user experience — ongoing, cross-cutting requirement

Treat UX as a requirement across the public website, course catalogue, course/offer pages, micro-courses, member area, learning room, lesson and interactive ChartLab flows, checkout/account flows, resource library, glossary, and responsive layouts. Do not leave UX review until the very end.

Use the established TradeThesis direction: clear, calm, warm, professional, honest, low-noise, compact, and editorial rather than generic SaaS or a trading terminal. Prefer a light visual theme, readable typography, sensible content width, efficient use of space, consistent navigation and spacing, and strong mobile behaviour.

Review each relevant flow for:
- clear information hierarchy and plain-language labels;
- orientation (“where am I, what is next, and how do I get back?”);
- readable charts, diagrams, annotations, images and long-form lesson content, including open/zoom controls where needed;
- accessible text contrast, focus states, keyboard/touch use, labels and meaningful alt text;
- consistent navigation, buttons, page rhythm, headings and reusable components;
- empty, loading, error, locked, completed and success states that explain what happened and what the learner can do next;
- responsive desktop/tablet/mobile presentation, avoiding cramped or hidden controls;
- honest distinctions between prototype/demo behaviour and features backed by persistence, permissions or payments.

Record material issues and fixes in the existing review/acceptance notes instead of making untracked visual changes. Recheck public site previews and the learning-room preview after changes.

### 3. Growing catalogue and course development status — ongoing product requirement

The course catalogue is not a fixed or complete list. Course development is ongoing, and additional courses/micro-courses are expected to be added over time. Treat this as a continuing product requirement, not a one-time copy change.

- Keep the catalogue architecture expandable so a new course can be added through data/content records and a reusable page/card template, without redesigning the whole site.
- Distinguish draft, in-development, preview, published/available, and archived states. Do not imply a course is available to buy or study merely because its card or source files exist.
- Public pages should communicate that the catalogue is growing and that new courses will be added as they're ready for learners. Course-specific availability and commercial details must remain accurate.
- Avoid hard-coded counts, filters or category totals that become incorrect when courses are added; derive them from the rendered/published catalogue where possible.
- Keep each course's curriculum, price, access rules, community inclusion and delivery model separate. New course additions must not accidentally inherit another course's permissions or offer.
- The eventual admin dashboard should make it straightforward for an authorised editor to create a draft course, add modules/lessons/assets, preview it, complete release checks and publish it without editing JavaScript or HTML manually.

This requirement applies across the public catalogue, member area and future admin workflows.

### 2. Friendly admin dashboard — explicitly deferred until near the end

Build a user-friendly, purpose-built TradeThesis admin/dashboard experience after the core learner-facing experience, content integration, authentication/entitlement flows and critical UX fixes are stable. This is a planned product milestone, not an immediate implementation task.

The intended dashboard should make routine work easy for a non-technical site administrator. Start with a short information architecture and workflow review before implementation. Consider:
- overview: courses/offers, learner activity and items needing attention;
- course and micro-course catalogue management;
- modules, lessons, lesson ordering, publication/draft status, preview and scheduling/drip status;
- media, charts, downloads and asset visibility;
- learner enrolments/entitlements and progress, with safe and auditable corrections;
- orders/payments/refunds and purchase-to-access troubleshooting, subject to the eventual backend;
- assessment/reveal and instructor-only material controls;
- search, filters, bulk-safe actions and clear confirmation for destructive operations;
- role-appropriate permissions, audit trail, accessible forms, useful validation, and clear empty/error/success states.

This is a planning scope, not a commitment that each item is already backed by the current static prototype. Do not expose answer keys, instructor-only notes or paid lesson bodies through client-side hiding. Only show live metrics/actions when connected to verified backend data; label placeholders/demo data honestly. Prefer extending the eventual production stack and its existing admin/auth conventions rather than inventing a disconnected second source of truth.

## Suggested order of work

1. Continue core course/learning-room and content integration work on `my-new-branch`; preserve existing micro-course material.
2. Audit and improve UX continuously as each path is implemented. Prioritize legibility of charts/images/annotations and zoom/open-at-readable-size affordances.
3. Stabilize authentication, entitlements, progress persistence, payment/access flows, instructor-only content separation and their acceptance tests.
4. Near the end, write the admin workflow map and UX wireframe, then implement and test the friendly admin dashboard against the real backend/data model.
5. Run a final sitewide UX pass across public pages, catalogue, micro-courses, account/member area, checkout, learning room and admin; review desktop and mobile previews and record results.

## Non-negotiable working rules

- Source of truth for current work: `prototypeweb` branch `my-new-branch`. Do not continue feature development on the separate `test` repository as the target.
- Preserve the existing course curriculum, micro-course assets, lesson source and agreed product positioning.
- Do not expose paid content or instructor-only keys in a public static deployment.
- Do not claim authentication, persistence, access control, payment handling, scheduling, grading or admin actions are production-ready until verified.
- Keep changes on the feature branch; do not merge/deploy or commit to `main` without explicit approval.
