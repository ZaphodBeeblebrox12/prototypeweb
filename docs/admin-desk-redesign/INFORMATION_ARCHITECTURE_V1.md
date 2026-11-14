# Admin Desk — Information Architecture v1

**Status:** Top-level domain grouping approved; submenu structure proposed for review  
**Date:** 2026-11-14  
**Branch:** `admin-desk-redesign-planning`

## 1. Approved top-level structure

The owner confirmed that this six-domain grouping reflects how TradeThesis is operated. The order below is the approved navigation order.

1. **Command Centre**
2. **Academy**
3. **Customers**
4. **Revenue**
5. **Growth**
6. **Platform**

This approval is specifically for the six top-level domains and their order. It does not yet approve every child item, label, count, permission rule or screen design below.

## 2. Proposed submenu structure

### Command Centre — run the day

- **Overview** — action-first view of cross-domain work requiring attention.
- **My Work** — proposed personal task view. Do not imply a new assignment system exists until the actual task/ownership model is audited.
- **Notifications** — proposed staff notification/alert entry. Existing member notification infrastructure is not proof of an admin alert centre.
- **Operations Timeline** — cross-domain stream of support clusters, job/provisioning events, domain events, audit and security signals, permission-scoped.

### Academy — manage learning products

- **Course Catalogue**
- **Course Approvals**
- **Course Builder** — link to the current supported authoring workflow; do not imply Tiptap is the production/default editor.
- **Offers & Access** — keep Course Offer ↔ Plan, price/currency, access duration and actual learner entitlement visibly distinct.
- **SEO & Discoverability**

### Customers — serve and understand learners

- **Learners & Accounts**
- **Support Tickets**
- **Customer 360** — detail access must remain permission-scoped; internal staff profiles are more restricted than learner profiles.

### Revenue — manage commercial operations

- **Payments & Refunds**
- **Subscriptions & Plans**
- **Invoices & Disputes**
- **Business & Finance**

Course-specific one-time offers remain distinguishable from recurring membership subscriptions, even if both are discoverable under Revenue as well as contextually from Academy.

### Growth — acquire and retain

- **Analytics**
- **Campaigns & Promotions**
- **Referrals & Rewards**
- **Gifts**
- **Email Delivery** — delivery logs and suppression are distinct from in-app notifications.

### Platform — maintain the service

- **Background Jobs**
- **Provisioning & Integrations**
- **Security & Audit**
- **Policies & Readiness**
- **Staff & Permissions** — exact capability and permitted actions require the role/permission audit.
- **Advanced Administration** — a clearly separated link to Django Admin during the phased migration.

## 3. Navigation behaviour to explore

- Persistent left sidebar on desktop; expanded and collapsed states.
- Mobile sidebar opens as a drawer and closes after destination selection.
- Domain headings remain visible and the active destination is unmistakable.
- Counts are reserved for actionable states and must be permission-aware. A count is not a decoration and must have a defined source, time window and meaning.
- The Command Centre may surface cross-domain exceptions, but the domain workspace remains the place where the operator resolves the underlying record.
- Global search should be designed across courses, learners, tickets, payments and operational records only where the user has access.
- Breadcrumbs should clarify deep navigation without duplicating the full sidebar hierarchy.
- Advanced Administration remains visible but visually secondary during migration; no existing capability is removed just because it is not yet represented in the new shell.

## 4. Important distinctions and guardrails

| Concept | Keep distinct from | Reason |
|---|---|---|
| Notifications | Work queue / assigned tasks | A notification informs; a task is work to complete. |
| Operations timeline | Background-job management | The timeline helps detect and understand; the Platform workspace manages detailed jobs and supported actions. |
| Course offer | Membership subscription plan | One-time course purchases and recurring membership commerce have different relationships and rules. |
| Offer / price | Learner entitlement | A purchasable offer is not proof that a learner currently has access. |
| Configuration present | Tested / operationally healthy | A setting being populated does not prove an end-to-end service works. |
| Course Builder | Admin course catalogue/review | Authoring, catalogue administration and editorial approval are related but different jobs. |
| Admin notifications | Existing member notifications | The current member notification model/API does not itself establish staff routing, severity or acknowledgement behaviour. |

## 5. Open decisions

- Whether My Work is genuinely a task queue in the first release or a filtered view of existing assigned support/review work.
- Whether Notifications is a staff inbox, an operational alert centre, or two distinct surfaces.
- Which counts belong beside navigation labels and what source/refresh/permission rules govern each.
- Whether Growth needs a different ordering or sub-grouping after persona/task validation.
- Which staff roles see each destination and which fields/actions they may use.
- Which Django Admin features migrate first, stay advanced, or should never be duplicated.
- Whether any high-frequency child destination needs a shortcut in the Command Centre.

## 6. Approval boundary

The six-domain grouping and order are approved. The submenu model above is a first-pass proposal to critique using the M01/M02 prototype and the Phase 0/1 route, role and task audit. It is not yet an implementation specification.
