# TradeThesis Admin Desk — Phase 0 Post-Deployment Permission Verification

**Verification date:** 15 November 2026 (Asia/Kolkata; exact browser-test time not captured)  
**Repository:** ZaphodBeeblebrox12/prototypeweb  
**Planning branch:** admin-desk-redesign-planning  
**Application source branch:** my-new-branch  
**Deployed source commit:** 294c173e8dd084c31595ac2d5aeab93d64f31481  
**Render service:** tradethesis-academy-staging  
**Render service ID:** srv-db9ioke1egvs73feb8ag  
**Render deployment:** dep-dbsa69m7bikc73f1opg0

## 1. Outcome

The security remediation is live on Academy staging and the owner supplied three authenticated, read-only browser-console runs for the targeted permission matrix.

**All 15 expected access decisions matched:**
- Non-staff learner: all five protected routes returned HTTP 403.
- Generic Django staff (application role=user, is_staff=true, is_admin=false): all five protected routes returned HTTP 403.
- Owner's main superuser account: all five protected routes returned HTTP 200.

This confirms the intended negative and positive access outcomes for these five GET routes on the deployed staging release. It is not a full penetration test or complete Phase 0 sign-off.

## 2. Deployment evidence

Render reported deployment `dep-dbsa69m7bikc73f1opg0` as `live`, finished at 2026-11-14 18:08:14 UTC. The deployment's commit object identifies the exact source commit `294c173e8dd084c31595ac2d5aeab93d64f31481`, the security remediation merge on `my-new-branch`.

The service is `https://tradethesis-academy-staging.onrender.com`. No production or public-static-staging deployment was triggered.

## 3. Read-only route results

All tests were same-origin GET requests using the browser's existing authenticated session. No POST/action was submitted and no account, gift, staff approval, ban, dispute, or other business data was modified.

| Route | Learner | Generic staff | Owner's superuser session |
|---|---:|---:|---:|
| `/growth/admin/referral-rewards/` | 403 | 403 | 200 |
| `/api/admin/staff-approvals/` | 403 | 403 | 200 |
| `/api/analytics/overview/` | 403 | 403 | 200 |
| `/admin/growth/send-gift/` | 403 | 403 | 200 |
| `/admin-disputes/` | 403 | 403 | 200 |
| **Expected outcomes matched** | **5/5** | **5/5** | **5/5** |

The learner and generic-staff transcripts were supplied by the owner and showed five explicit HTTP 403 responses in each session. The owner then supplied a main-superuser session transcript showing five HTTP 200 responses. The account label is owner-reported; these transcripts do not independently expose the Django `is_superuser` database field. The successful route access nevertheless confirms that this authenticated admin session is authorised for the tested endpoints.

A browser-console message of `Promise { <state>: "pending" }` is the immediate return value from the async script and is not a failed request; the subsequent per-route responses show completion. A separate `/favicon.ico` 404 is unrelated to the permission checks.

## 4. Interpretation and limits

- The learner denial on the referral rewards route confirms that the previous login-only Growth data exposure is closed for the tested learner session.
- The generic-staff denials confirm that `is_staff=true` alone no longer grants access to staff approvals, global analytics, gift sending, disputes, or referral rewards.
- The authorised admin session still reaches all five routes.
- The analytics overview returned 200 for the authorised admin session, resolving the previous observed 500 in this path at the HTTP level.
- Gift sending was tested only with GET. No gift was created and no email was sent.
- Staff approvals were tested only with GET. No staff member was approved or rejected.
- Disputes was tested only with GET. No dispute action was submitted.
- Referral reward and analytics checks establish route-level access only; the returned page/API data was not independently inspected for field-level minimisation.
- This matrix does not test Django Admin's global `/admin/` boundary. The planned superuser-only cutover remains deferred until replacement workflows have parity.
- This matrix does not settle specialist department permissions, Support object scoping, Academy authoring/review permission parity, or customer/finance record isolation.

## 5. Consolidated generic-staff route regression

A subsequent read-only browser-console audit was run in the generic staff session on 15 November 2026. The session was on `/dashboard/`; all checks used same-origin GET requests and no mutations.

**All 17 expected route decisions matched.**

| Area | Expected | Observed | Result |
|---|---:|---:|---|
| Command Centre | 200 | 200 | PASS |
| Operations | 200 | 200 | PASS |
| Support queue | 200 | 200 | PASS |
| Own notifications | 200 | 200 | PASS |
| Customers / Accounts | 403 | 403 | PASS |
| Academy review | 403 | 403 | PASS |
| Academy SEO | 403 | 403 | PASS |
| Legacy Course Builder | 403 | 403 | PASS |
| Tiptap Builder | 403 | 403 | PASS |
| Finance | 403 | 403 | PASS |
| Subscriptions | 403 | 403 | PASS |
| Business settings | 403 | 403 | PASS |
| Growth referral rewards | 403 | 403 | PASS |
| Growth gift sending | 403 | 403 | PASS |
| Disputes | 403 | 403 | PASS |
| Staff approvals API | 403 | 403 | PASS |
| Growth analytics | 403 | 403 | PASS |

Additional observations:
- Five ticket detail URLs discovered from the Support queue returned HTTP 200. This confirms access to those queue-visible tickets only; it does **not** prove that out-of-scope tickets are denied.
- No Platform job/provisioning detail links were found on the Operations page, so Platform detail access was not tested.
- Legacy Django Admin `/admin/` returned HTTP 200. This is expected for now because the global staff lockout remains deliberately deferred pending workflow parity; it is recorded as legacy access, not as one of the 17 expected passes.
- The script reported zero unexpected/review-required results. No action endpoint was submitted and no data was changed.

This completes the generic-staff core-route smoke test for Command Centre, Operations, Support queue and own notifications, and confirms denials for the tested restricted sections. It does not close Support object-scope review: an out-of-scope ticket fixture/ID still needs a deliberate negative test. Specialist-role permissions and Platform detail permissions also remain unverified.

## 6. Remaining Phase 0 work

1. **Support object scope:** test a known out-of-scope ticket fixture against the generic-staff session. The source audit identified an any-staff fallback when no ticket approvers are assigned; resolve the policy and verify the boundary.
2. **Specialist role matrix:** map and test actual Groups/model permissions for Academy, Revenue, Growth and Platform. These personas were not represented by the generic-staff account.
3. **Platform detail access:** test known job/provisioning detail fixtures for permitted and unpermitted staff roles.
4. **Django Admin cutover:** keep existing legacy access in place until workflow parity is demonstrated; do not globally lock out staff as part of this audit.
5. **Account cleanup:** after all required checks, remove only the disposable staging test accounts created for this audit and revoke their sessions. Do not delete or alter the owner's main account.

No additional application code, permissions, migrations, Render settings, deployments, merges, or rebases were changed as part of this verification.

**Updated status:** The three-persona / five-route security matrix and the 17-route generic-staff regression are verified on live Academy staging. Phase 0 remains open pending Support object-scope review, specialist-role mapping, Platform detail checks and final staging cleanup.


1. **Core staff workflow regression:** confirm generic staff can still reach the intended Command Centre, Operations and Support list routes. Verify expected read-only access and avoid any action submissions.
2. **Support object scope:** check only saved/known ticket fixture URLs; confirm generic staff visibility is consistent with the intended plan/approver policy. The source audit identified an any-staff fallback when no ticket approvers are assigned; this remains a policy question.
3. **Specialist role matrix:** map and test actual Groups/model permissions for Academy, Revenue, Growth and Platform. These personas were not represented by the generic-staff account.
4. **Django Admin cutover:** keep existing legacy access in place until workflow parity is demonstrated; do not globally lock out staff as part of this audit.
5. **Account cleanup:** after all required checks, remove only the disposable staging test accounts created for this audit and revoke their sessions. Do not delete or alter the owner's main account.

No additional application code, permissions, migrations, Render settings, deployments, merges, or rebases were changed as part of this verification.

**Status:** The targeted three-persona / five-route permission matrix is verified on live Academy staging. Phase 0 remains open pending core workflow regression, Support object-scope review, specialist-role mapping and final staging cleanup.
