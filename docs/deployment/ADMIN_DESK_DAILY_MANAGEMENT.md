# Admin Desk — daily management workflows

The TradeThesis Admin Desk is intended to be the creator-facing operating area. Django Admin remains a technical fallback for advanced or infrequent tasks.

## Owner-facing workflows
- Learner directory and details: search customers, inspect community connections, current access, recent payments and history; ban/unban, activate/deactivate and send a password-reset email.
- Subscription/access worklist: filter access records, extend active access, cancel immediately, and grant complimentary access only from active hidden plans with a reason.
- Payments and invoice register: search read-only financial records, inspect transaction references, and print/save an immutable invoice snapshot.
- Business settings: edit seller/legal identity, address, support email, invoice prefix, and simple tax settings used for new checkouts/invoices. Enabling tax requires an explicit confirmation.

## Intentionally not duplicated
Provider refund processing, webhook troubleshooting, jobs internals, staff permissions and versioned legal-policy publishing remain in their specialist tools for now. Course authoring is a separate creator-friendly editor workstream and should not be duplicated with another Django-form editor.

## Safety and verification
The views require active staff login and relevant model permissions. Staff/superuser records are excluded from the customer directory. Subscription lifecycle services record history and queue access reconciliation. Granting access requires an active hidden plan and a reason. Payments and invoices are read-only in this workspace. Run backend CI and then perform an authenticated staging acceptance pass on desktop and mobile.
