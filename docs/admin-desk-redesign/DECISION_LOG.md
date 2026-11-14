# Admin Desk Redesign — Decision Log

**Status:** Open for brainstorming  
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

## Decisions to make together

### 1. Navigation hierarchy
- [ ] Approve the proposed groups: Command Centre, Academy, Customers, Revenue, Growth, Platform.
- [ ] Decide whether Growth is top-level or nested.
- [ ] Decide which advanced actions remain in Django Admin for the first release.
- Notes:

### 2. Overview philosophy
- [ ] Action queue first.
- [ ] Operational cockpit.
- [ ] Personal workbench.
- [ ] Hybrid.
- Notes:

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

For each decision, record:

- **Decision:**
- **Options considered:**
- **Chosen option:**
- **Reason:**
- **Affected screens/workflows:**
- **Open risks:**
- **Approved by:**
- **Date:**
