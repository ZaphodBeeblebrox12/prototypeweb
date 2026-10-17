# TradeThesis Admin Desk — Milestone 1

**Repository:** `ZaphodBeeblebrox12/prototypeweb`  
**Branch:** `my-new-branch`  
**Original implementation baseline:** `ae1f93add560109e365ea8e7a194a400baea6bfe`  
**Route:** `/staff/admin-desk/`  
**Status:** Implemented and verified in backend CI.
**Code commit verified by CI:** `00f208d7b3238903603f7daa361a1551fdf98260`.
**CI:** [Run 39070357094](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39070357094) — success on Python 3.11 and 3.12. Each full suite: 699 passed, 213 warnings, 11 subtests passed. The focused Academy regression: 15 passed, 9 warnings, 4 subtests passed.
**Deployment/staging browser check:** not performed.

## What this milestone adds

- A staff-only operations page with a direct path back to Django administration.
- A light, compact, responsive layout designed to sit alongside the existing Django admin rather than replace it.
- Permission-filtered payment, subscription, Telegram/access-audit and background-job indicators, reusing the existing helper.
- Course catalogue counts and links for users authorised to manage shared course content.
- Current published-lesson, course-offer, entitlement, learner-completion and course-import review counts from database records.
- Focused tests for real course counts, authorised admin links, learner denial and staff without course-content authority.
- An Admin Desk link from the existing Django grouped admin index.

## Safety boundaries

The desk is read-only. Publishing, importing, entitlement grants, payment changes, user changes and destructive operations remain in existing Django admin forms and policies. Per-model Django admin links are included only when the registered admin grants view permission. Course metrics are omitted unless the account is permitted to administer course content.

The pre-existing `/staff/ops/` payments operations cockpit is intentionally unchanged. The Admin Desk has its own `/staff/admin-desk/` route so it cannot shadow existing payment reconciliation, worklist, alert or revenue screens.

## Verification checklist

- Python syntax compilation for changed Python files.
- Admin Desk regression tests for access control and real counts.
- Full backend CI passed on code commit `00f208d7b3238903603f7daa361a1551fdf98260`, across Python 3.11 and 3.12.
- The existing `/staff/ops/` payments cockpit tests pass after the Admin Desk route was separated.
- Staging/manual browser verification is deliberately separate and has not been performed. No deployment was triggered.
