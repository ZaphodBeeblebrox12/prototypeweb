# Admin Desk Redesign — Mockup Register

**Status:** Planned; no production implementation  
**Branch:** `admin-desk-redesign-planning`

Use this register to keep design work deliberate and reviewable. Each mockup should have a version, target viewport, assumptions, data provenance and feedback record.

## Mockup sequence

| ID | Screen / artefact | Required concepts or states | Priority | Status |
|---|---|---|---|---|
| M00 | Current-state reference board | Existing Admin Desk, shared nav, Django Admin boundary, key current routes | P0 | Not started |
| M01 | Global application shell | Expanded/collapsed sidebar, top bar, breadcrumbs, search, notification entry, mobile menu | P0 | V1 drafted — review pending |
| M02 | Command Centre | Three alternatives: action queue, operational cockpit, personal workbench | P0 | V1 drafted — review pending |
| M03 | Academy landing | Course catalogue summary, approvals and course health | P0 | Not started |
| M04 | Course catalogue | Flagship/supporting/mini/hidden; lifecycle; access type; filters and density | P0 | Not started |
| M05 | Course detail / control page | Content, catalogue role, access model, modules/lessons, linked offers, readiness | P0 | Not started |
| M06 | Approval queue | New vs revision, author, submitted time, review status, missing assets | P0 | Not started |
| M07 | Course review detail | Preview, outline, assets, validation, approve, return with mandatory feedback | P0 | Not started |
| M08 | Offers & pricing | Course-offer ↔ Plan, one-time price, geo-pricing, duration, active status | P0 | Not started |
| M09 | Learner access | Entitlements, scheduled/active/expired/revoked, event history, safe grant/revoke | P1 | Not started |
| M10 | Support queue | SLA, priority, category, assignment, mine/unassigned, filters | P0 | Not started |
| M11 | Ticket detail | Conversation, attachments, public reply, internal note, approval/rejection, reassignment | P0 | Not started |
| M12 | Learners & accounts | Search, account state, safe actions, list density | P1 | Not started |
| M13 | Customer 360 | Course progress/access, subscription/payment, support, community, security restrictions | P0 | Not started |
| M14 | Revenue overview | Payments, subscriptions, invoices, refunds/disputes | P1 | Not started |
| M15 | Business readiness | Seller/invoice/legal/payment/email/runtime checks; configured vs tested | P1 | Not started |
| M16 | Operations overview | Incident severity, affected customers, issue clusters, time range | P0 | Not started |
| M17 | Jobs & provisioning | Queue states, attempts, lock age, unknown external state, error detail | P1 | Not started |
| M18 | Growth & analytics | Signups, campaigns, promotions, referrals, gifts, email delivery/suppression | P2 | Not started |
| M19 | Notifications / attention | Event source, recipient, severity, read/acknowledged, deduplication, deep link | P0 | Not started |
| M20 | Policies / audit / security | Readiness, policy versions, audit timeline, permission-scoped security views | P1 | Not started |
| M21 | Responsive design board | Tablet, mobile navigation, dense tables, ticket actions, drawers and dialogs | P0 | Not started |
| M22 | Component and visual system | Typography, spacing, tables, statuses, forms, menus, dialogs, toasts, empty/error states | P0 | Not started |
| M23 | Clickable prototype | End-to-end priority journeys using clearly labelled illustrative data | P0 | Not started |

## Required annotations on every mockup

1. Screen purpose and primary user.
2. Main task(s) the screen supports.
3. Route(s) or proposed route.
4. Existing backend data and action(s) being represented.
5. Permission assumptions.
6. Empty, loading, error, no-access and success states.
7. Responsive behaviour.
8. What is illustrative, proposed or currently unsupported.
9. Outstanding questions.
10. Review notes and approval status.

## Review checklist

- [ ] Does the screen preserve every relevant existing action?
- [ ] Is the most important next action obvious?
- [ ] Are labels consistent with backend terminology?
- [ ] Are priority/SLA/status values clear without relying on colour alone?
- [ ] Are permissions reflected in the design and still enforced server-side later?
- [ ] Are destructive, financial, publishing and access actions treated carefully?
- [ ] Does the design expose only the data appropriate to the role?
- [ ] Can the screen handle long text, empty data and high-volume lists?
- [ ] Has desktop and mobile behaviour been reviewed?
- [ ] Is the screen consistent with the approved visual system?

## Prototype safety

HTML mockups must use local illustrative data and simulated interactions only. They must not make live API calls or perform actions against staging/production data. Every mockup must visibly state that its sample records are illustrative.

## First design pass — 14 November 2026

- **M01:** Shared application shell using the approved six-domain order. Includes desktop sidebar, mobile drawer, global search field, breadcrumb, notification entry point, staff context and a separate Advanced Administration link for the migration period.
- **M02:** Three switchable overview directions: (1) action queue first, (2) operational cockpit, and (3) personal workbench. The action-queue direction is the recommended candidate for discussion, not a final design approval.
- **Prototype artifact:** `tradethesis_admin_shell_command_centre_v1.html` (standalone HTML, supplied in the design review conversation).
- **Viewport intent:** Desktop-first at approximately 1440px, with tablet/mobile responsive behaviour included in the prototype.
- **Data safety:** All names, counts, IDs, queue entries and times are fictional illustrative data. No live APIs or backend actions are connected.
- **Current visual direction:** Warm light, compact/editorial, restrained terracotta accent, thin borders, low card usage and dense but readable queue rows.
- **Outstanding review:** Sidebar content/order below the six approved domains; balance and placement of overview context; task prioritisation, ownership and notification semantics; top-bar controls; small-screen navigation.
