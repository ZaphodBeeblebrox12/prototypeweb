# Admin Desk Redesign — Decision Log

**Status:** Open for brainstorming and mockup validation  
**Branch:** `admin-desk-redesign-planning`  
**Rule:** No implementation decisions are considered approved unless recorded here with an owner/date and explicit status.

## Guardrails already agreed

| Item | Current position | Status |
|---|---|---|
| Work mode | Planning, brainstorming and mockups before implementation | Agreed |
| Code changes | No app-code changes in this branch | Agreed |
| Baseline | Current Academy staging source on `my-new-branch` | Provisional baseline; re-verify before implementation |
| Existing workflows | Preserve current permissions and business rules | Non-negotiable |
| Previous HTML redesign | Exploratory design only, not a specification | Agreed |
| Tiptap | Do not assume it is the default integrated authoring path | Non-negotiable until separately approved |

## Confirmed direction

### Decision 1 — One unified Admin Desk

- **Decision:** The Admin Desk should behave as one unified operating workspace.
- **Options considered:** Separate destinations for Academy, customers, revenue and platform operations; or one shared application shell and sidebar.
- **Chosen option:** One shared Admin Desk shell and sidebar. The proposed domains are Command Centre, Academy, Customers, Revenue, Growth and Platform.
- **Reason:** Staff should be able to move between core operating functions without feeling they are entering disconnected administration products.
- **Affected screens/workflows:** Global navigation, page shell, overview, Academy, customer support, commerce, growth tools, operations and settings.
- **Open risks:** The exact grouping, labels, nesting, role-based visibility and responsive sidebar behaviour still need to be designed and validated.
- **Approved by:** User
- **Date:** 2026-11-14

### Decision 2 — Action-first landing page

- **Decision:** The Admin Desk landing page should prioritise work that needs attention or action, rather than leading with business metrics.
- **Options considered:** Metrics dashboard, operational cockpit, personal workbench, or a hybrid.
- **Chosen option:** Action queue first. Key metrics may provide context, but should not displace urgent work, blocked items, pending decisions or operational exceptions.
- **Reason:** The first screen should answer “What needs my attention now?” before “How is the business performing?”
- **Affected screens/workflows:** Command Centre overview, alerts, approvals, support, failed/stalled jobs and other pending operational work.
- **Open risks:** We still need to define prioritisation, grouping, ownership, urgency, stale-item handling and which items are visible to each staff role.
- **Approved by:** User
- **Date:** 2026-11-14

### Decision 3 — Phased migration from Django Admin

- **Decision:** Bring everyday administration into the unified Admin Desk gradually, while retaining a separate Advanced Administration destination for Django Admin capabilities that have not yet been safely replaced.
- **Options considered:** Migrate everything before launch; keep Django Admin as the permanent primary destination; or migrate by workflow while retaining a temporary/long-tail advanced destination.
- **Chosen option:** Phased migration by workflow. The new Admin Desk becomes the primary experience for migrated day-to-day work. Django Admin remains accessible for advanced or low-frequency configuration until an equivalent, permission-safe experience exists in the new interface.
- **Reason:** This avoids a risky all-at-once rewrite and prevents the redesign from hiding or breaking important existing administrative capabilities.
- **Affected screens/workflows:** Navigation, staff permissions, advanced configuration, data maintenance, operational controls and the migration plan.
- **Open risks:** We must identify every Django Admin feature, its users and risk level; define ownership for each migration; and avoid duplicate or conflicting controls during transition.
- **Approved by:** User
- **Date:** 2026-11-14

### Decision 4 — Six-domain information architecture

- **Decision:** Use six top-level domains in the shared Admin Desk navigation.
- **Options considered:** Separate administration destinations; fewer consolidated domains; or the six-domain model.
- **Chosen option:** Command Centre, Academy, Customers, Revenue, Growth and Platform, in that order.
- **Reason:** This matches how the owner thinks about operating TradeThesis and keeps the six major responsibilities distinct inside one coherent workspace.
- **Affected screens/workflows:** Global sidebar, breadcrumbs, Command Centre overview, domain landing pages and cross-domain links.
- **Open risks:** The top-level grouping and order are approved; submenu labels, exact destinations, role-based visibility, counts and mobile navigation remain design decisions to validate.
- **Approved by:** User
- **Date:** 2026-11-14

## Decisions still to make together

### 1. Navigation hierarchy
- [x] Use one shared sidebar for the Admin Desk domains.
- [x] Approve the six top-level domains and their order: Command Centre, Academy, Customers, Revenue, Growth, Platform.
- [ ] Finalise submenu labels, destinations, nesting and role-based visibility.
- [ ] Define role-based visibility and the location/label for Advanced Administration.
- Notes: The six-domain grouping/order is approved. The submenu-level information architecture remains open.

### 2. Overview philosophy
- [x] Action queue first.
- [ ] Decide the supporting mix of operational context, personal workbench elements and business metrics.
- [ ] Define priority rules and how work is assigned or claimed.
- Notes: Metrics are supporting context, not the primary purpose of the landing page.

### 3. Notifications and alerts
- [ ] Personal notification inbox.
- [ ] Operational alert centre.
- [ ] Assigned task queue.
- [ ] Separate inbox and alert centre.
- [ ] Define critical vs warning vs informational events.
- Notes:

### 4. Support and Customer 360
- [ ] Customer 360 as full page.
- [ ] Customer 360 as contextual side panel.
- [ ] Both.
- [ ] Define which customer details appear inline in ticket review.
- Notes:

### 5. Academy workspace
- [ ] Catalogue table/list/hybrid.
- [ ] Unified course detail workspace vs launchpad into existing screens.
- [ ] Separate approvals queue and full review detail.
- [ ] Keep Course Builder separate from Admin Desk shell.
- Notes:

### 6. Commerce and access
- [ ] One commerce workspace with clearly separated course and membership commerce.
- [ ] Separate Course Offers and Subscriptions/Plans workspaces.
- [ ] Define how geo-pricing and access duration should be presented.
- Notes:

### 7. Staff and permissions
- [ ] Show current staff role and permission summary.
- [ ] Allow staff/permission administration in the redesigned Admin Desk.
- [ ] Keep permission changes in Django Admin initially.
- Notes:

### 8. Visual direction
- [ ] Warm light / editorial.
- [ ] Neutral light / data-dense.
- [ ] Other direction to explore.
- [ ] Density preference and target desktop width.
- Notes:

## Decision record format

For each future decision, record:

- **Decision:**
- **Options considered:**
- **Chosen option:**
- **Reason:**
- **Affected screens/workflows:**
- **Open risks:**
- **Approved by:**
- **Date:**
