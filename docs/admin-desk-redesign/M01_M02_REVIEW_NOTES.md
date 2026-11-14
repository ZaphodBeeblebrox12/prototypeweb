# M01 + M02 — First Prototype Review Notes

**Version:** v1  
**Date:** 2026-11-14  
**Status:** Ready for owner review; not approved for implementation  
**Prototype:** `tradethesis_admin_shell_command_centre_v1.html` (standalone artifact supplied in the design review conversation)

## Scope

This first prototype combines:

- **M01 — Global application shell:** shared TradeThesis Admin Desk shell, six approved top-level domains, top bar, breadcrumbs, global-search field, notification entry point, staff context, desktop expanded/collapsed sidebar and mobile drawer.
- **M02 — Command Centre:** three switchable overview directions inside the same shell.

It is a design prototype only. It has no live API calls, database access, real staff identity, authentication, permission checks, or mutating actions.

## The three overview directions

### 01 — Action queue first (recommended candidate)

The main area is a prioritized queue. The operator sees urgent and overdue work, tasks due soon and blocked decisions before secondary context. A compact six-domain snapshot and recent activity sit alongside the queue.

**Why it is the leading candidate:** It directly implements the agreed landing-page principle: “What needs my attention now?” It supports fast triage without turning the top of the page into a wall of KPIs.

**Risk to test:** The order must be based on meaningful severity, impact, SLA and time sensitivity, not arbitrary static weights. Work must show ownership or unassigned status, affected record, age/due state and a safe next step.

### 02 — Operational cockpit

The six domains appear as compact health summaries, followed by a cross-domain exception stream.

**Strength:** Strong at-a-glance operational monitoring and spotting where the system is unhealthy.

**Risk:** A matrix of domain status indicators may make individual tasks less visible and drift back toward a metrics dashboard.

### 03 — Personal workbench

The first screen centres on tasks assigned to the current staff member, personal follow-ups, recent records and shortcuts.

**Strength:** Useful for staff who work from a stable personal queue.

**Risk:** It can hide team-wide incidents or unassigned work. It also assumes a reliable assignment/task model, which must be confirmed in the current system before the UI promises one.

## Current recommendation

Continue with **Direction 01 — Action queue first**, but borrow two elements from the alternatives:

- From the operational cockpit: a narrow, secondary cross-domain pulse and a meaningful operations timeline.
- From the personal workbench: a clear “My Work” filter or destination, but only if it can be backed by existing assignment semantics or an explicitly approved future capability.

Do not merge all three concepts into one crowded dashboard. Keep the first screen decisive.

## Shell decisions represented

- Top-level order follows the approved structure: Command Centre, Academy, Customers, Revenue, Growth, Platform.
- Command Centre currently proposes Overview, My Work, Notifications and Operations Timeline.
- Platform currently proposes Background Jobs, Provisioning & Integrations, Security & Audit and Staff & Permissions.
- Advanced Administration remains separate and secondary during the migration period.
- Desktop sidebar supports expanded and collapsed states; mobile uses a drawer.
- Global search is a design placeholder; its scope and permission-aware result behaviour remain to be specified.
- Notifications panel is explicitly labelled illustrative and notes the gap between member notification infrastructure and a real staff alert feed.

## Data and workflow annotation

All people, identifiers, timestamps, queue counts, job names and record states in the HTML are invented solely to make layout decisions tangible. The HTML banner identifies the data as illustrative. No sample item should be read as a real open ticket, payment, course review, email event or platform incident.

Existing source-level concepts represented in the mockup include course review, support ticket SLA, payment/entitlement reconciliation, background jobs, provisioning state and email delivery records. Their exact data shape, current route, permission conditions and available actions must be verified in the route/capability and role matrix before detailed design sign-off.

No publishing, refunding, granting/revoking access, replying to members, changing permissions or retrying jobs is implemented or simulated as a real mutation. Clicks only show prototype explanatory messages.

## What this v1 does not yet solve

- Complete route inventory and staff-role permission map.
- Proper search results, recent searches, keyboard navigation and empty/error states.
- Real admin notifications: event sources, staff recipients, severity, acknowledgement, deduplication, read semantics and escalation.
- Task ownership/claiming and whether all action types can be assigned.
- Full queue sorting logic, SLA countdown semantics and stale-item rules.
- Detailed Academy, Support, Revenue, Growth and Platform destination screens.
- Tablet/narrow-screen review beyond initial responsive layout.
- Accessibility review with keyboard-only navigation, contrast measurement and screen readers.
- Reconciliation of every child route with the existing sitewide navigation and Django Admin boundary.

## Review prompts

1. Does the sidebar feel like the right hierarchy and density, especially when all six domains are expanded?
2. Is the Command Centre action queue the correct first screen, or should the operational cockpit be the default?
3. Should the compact six-domain pulse remain beside the queue, or be reduced further?
4. Is Operations Timeline correctly placed under Command Centre, with Background Jobs and Provisioning under Platform?
5. Does “My Work” deserve a first-level item before we establish which existing work can be assigned?
6. Should notifications open a small popover, a dedicated attention page, or a distinct inbox/alert centre?
7. What information is missing from each queue row before an operator can decide what to do safely?

## Next design step after review

Revise M01/M02 based on feedback. Then move to M03 Academy landing and M10 Support queue as two contrasting domain workspaces. Before finalising their detailed workflows, complete the relevant current-state route and permission audit rather than inventing missing capabilities.
