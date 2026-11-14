# Customers Workspace — V1 Review Notes

**Date:** 2026-11-14  
**Status:** Draft for owner review; no implementation approval  
**Prototype:** `tradethesis_admin_customers_workspace_v1.html`

## What this pass covers

- M27 Customers Overview.
- M12 Learners & Accounts.
- M28 Learner Account Detail.
- M10 Support Tickets.
- M11 Ticket Detail.
- M13 Customer 360.

The shared shell uses the approved V2 visual language. The six top-level domains remain unchanged.

## Decisions preserved from source

- The general account list excludes staff and superusers.
- Account search/filter/sort/pagination reflect the existing view.
- Account writes require `accounts.change_user`; ban/deactivate require a reason of at least five characters, with audit and reconciliation.
- The support queue is reviewer-scoped; the current list order remains newest first.
- First-response SLA targets remain 2h / 8h / 24h / 72h by priority.
- Ticket status/category/priority/assignment values use the model values.
- Internal `TicketMessage` is append-only and private; public staff reply moves an open ticket to Awaiting Member.
- Rejection requires a reason; reopening preserves the old reviewer summary as a private message and is blocked by another active ticket in the same user/category.
- Approving an access request grants the eligible hidden Plan and enqueues reconciliation in the same transaction; billing/technical approval resolves the ticket without granting a plan.
- Customer 360 uses ticket reviewer scope or account-view permission, then independently gates subscription, payment, invoice, Academy and security records.
- Internal staff requester profiles are limited to identity and reviewer-visible tickets.
- Managed Telegram/Discord account link state is not inferred from legacy login-verification fields.
- Internal support notes and raw security/payment identifiers stay out of the Customer 360 activity view.

## Design choices introduced for review

- One Customers Overview as a compact action-first entry point.
- A distinct Learners & Accounts list and Learner Account Detail page.
- A distinct Support Tickets queue and Ticket Detail page.
- Customer 360 remains a full-page read-only relationship view.
- Ticket Detail includes a compact customer context panel linking to Customer 360.
- The Customer 360 prototype uses internal tabs for Overview, Learning & Access, Revenue, Support, Community & Security and Activity.
- A local display-only toggle demonstrates the internal-staff requester restriction.
- The current newest-first queue default is preserved. Priority/SLA-first sorting is not silently introduced.

## Important terminology point

The existing `admin_notes` field is not the same as an internal conversation note. It is the reviewer/resolution summary used in the ticket approval/rejection notification and is shown in the reviewer template after closure. A private internal note is a separate append-only `TicketMessage` with `is_internal=True`. The design keeps those visually distinct.

## Browser validation

- Search/filter interaction passed.
- Ticket detail navigation passed.
- Public reply and internal-note composer switching passed.
- Customer 360 tabs passed.
- Internal-account restriction preview passed.
- Learner search and account-detail handoff passed.
- Mobile drawer open/navigation/close passed.
- No page errors in the exercised paths.
- 390px viewport shows no horizontal page overflow.

## Not tested / not claimed

- Authenticated live staging visual parity.
- All staff role/group permission combinations.
- API/DB integration, real ticket writes or account actions.
- Screen-reader/keyboard-only accessibility audit.
- Contrast certification.
- Actual external community provisioning repair flow.
- Full responsive testing across tablet and other mobile sizes.

## Review prompts

1. Is the distinction between Account Detail and Customer 360 helpful?
2. Should the account list or customer profile be the default Customers landing destination for staff?
3. Is the queue priority information sufficiently visible without changing its current newest-first order?
4. Is the ticket detail action rail understandable for access requests versus billing/technical issues?
5. Does Customer 360 make permission gaps and internal staff restrictions clear enough?
6. Do the cross-domain links show the right boundaries?

## Next step

Revise the Customers screens from owner feedback. Then design Revenue, using the same sample learner, support ticket, course purchases, membership subscription, payments and invoices to ensure one coherent relationship across Customers, Academy and Revenue.
