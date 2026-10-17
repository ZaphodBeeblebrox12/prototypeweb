# TradeThesis Admin Desk — Milestone 1

**Repository:** `ZaphodBeeblebrox12/prototypeweb`  
**Branch:** `my-new-branch`  
**Baseline:** `ae1f93add560109e365ea8e7a194a400baea6bfe`  
**Scope:** read-only staff Admin Desk at `/staff/ops/`  
**Deployment:** not performed.

## What this milestone adds

- A staff-only operations page with a direct path back to Django administration.
- A light, compact, responsive layout designed to sit alongside the existing Django admin rather than replace it.
- Permission-filtered payment, subscription, Telegram/access-audit and background-job indicators, reusing the existing helper.
- Course catalogue counts and links for users authorised to manage shared course content.
- Current published-lesson, course-offer, entitlement, learner-completion and course-import review counts from database records.
- Focused tests for real course counts, authorised admin links, learner denial and staff without course-content authority.
- A named route for the existing `/staff/ops/` link.

## Safety boundaries

The desk is read-only. Publishing, importing, entitlement grants, payment changes, user changes and destructive operations remain in existing Django admin forms and policies. Per-model Django admin links are included only when the registered admin grants view permission. Course metrics are omitted unless the account is permitted to administer course content.

## Verification checklist

- Python syntax compilation for the changed Python files.
- Django Admin Desk regression tests.
- Full backend CI on this commit, including both configured Python versions.
- Staging/manual browser verification is deliberately separate and has not been performed. No deployment was triggered.
