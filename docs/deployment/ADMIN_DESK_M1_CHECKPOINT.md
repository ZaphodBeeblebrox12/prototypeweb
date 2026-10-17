# TradeThesis Admin Desk — Milestone 1

**Repository:** `ZaphodBeeblebrox12/prototypeweb`  
**Branch:** `my-new-branch`  
**Original implementation baseline:** `ae1f93add560109e365ea8e7a194a400baea6bfe`  
**Route:** `/staff/admin-desk/`  
**Status:** Deployed to staging; CI green. Authenticated browser acceptance remains pending.
**Code commit verified by CI:** `00f208d7b3238903603f7daa361a1551fdf98260`.
**CI:** [Run 39070357094](https://github.com/ZaphodBeeblebrox12/prototypeweb/actions/runs/39070357094) — success on Python 3.11 and 3.12. Each full suite: 699 passed, 213 warnings, 11 subtests passed. The focused Academy regression: 15 passed, 9 warnings, 4 subtests passed.
**Render staging service:** `tradethesis-academy-staging` (`srv-db9ioke1egvs73feb8ag`).  
**Deployment:** `dep-db9uic61egvs738ma45g`, status `live`, from branch head `1329867c081cdd1ac5b96dab833b57d4ce402f69`. Started `2026-10-17T21:31:28Z`, finished `2026-10-17T21:33:14Z`.  
**Server health:** new instance started Gunicorn and Render logged `GET /health/` HTTP 200 at `2026-10-17T21:33:17Z`. No error/warning-level app logs were returned in the `21:33–21:35Z` check window.  
**Browser limitation:** this execution environment could not resolve/access the public Render hostname. I could not independently verify authenticated HTML rendering of `/staff/admin-desk/`, `/staff/ops/` or `/admin/`; a logged-in browser spot-check remains pending.

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
- Render staging deployment is live and health-probe checks passed. Authenticated route and visual acceptance remain a manual follow-up because the public host was inaccessible from this execution environment.
