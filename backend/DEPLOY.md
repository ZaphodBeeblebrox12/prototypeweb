# TradeThesis Django deployment notes

**Status: not approved for production deployment.** The Django backend is being integrated through draft PR #4 into `ZaphodBeeblebrox12/prototypeweb`. The learner journey, catalogue seed, payment/access lifecycle, content protection and production routing have not been verified end to end.

## Repository and branch rules

- During this integration, work on `feature/tradethesis-academy` and keep PR #4 targeted to `my-new-branch`.
- The only permitted integration target is `my-new-branch`.
- Do not push, merge, or deploy feature work to `main`.
- Do not treat the existence of `render.yaml`, a successful Django check, or a preview page as evidence of a live service.

## Before deployment

1. **Choose and verify routing.** The preferred setup serves the public TradeThesis site and Django `/learn/`, `/accounts/`, checkout and protected media routes on one origin. A separate learning host is possible, but session cookies, redirects, CSRF, allowed hosts and callback URLs must then be configured and tested explicitly. The production host/domain is not established by this repository.
2. **Protect source material.** This GitHub repository is currently public and contains paid course source and internal instructional material. Private lesson bodies, answer keys and protected downloads cannot be secured merely by adding Django views while the source stays publicly readable. Before selling, make the source repository private or move confidential source/assets into private storage and verify the public build excludes them.
3. **Use production infrastructure.** Configure persistent PostgreSQL, production settings, HTTPS, secure session/CSRF cookies, allowed hosts, static/media storage and backups. Do not use a local SQLite database or an ephemeral filesystem for learner/payment records.
4. **Configure real services using deployment secrets.** Set `SECRET_KEY`, `DATABASE_URL`, email delivery, payment provider credentials and verified webhooks, OAuth credentials and any bot integrations that are actually required. Do not commit secrets or reuse development webhook secrets.
5. **Configure catalogue and offers.** Reconcile approved course manifests against Django records. Keep Trading Path, Support & Resistance, Volume Price Analysis, CONSTRUCT, live classroom and micro-courses distinct. The latest validators confirm the source mapping (30 Trading Path lessons, 18 Support & Resistance lessons and 30 VPA lessons), but the default validation commands do not create database records. Do not activate offers for drafts or incomplete material. The separate 12-calendar-month CONSTRUCT community entitlement and refund/revoke logic are implemented and covered by tests; before sale, create the dedicated hidden one-time Plan, CourseOffer and channel mappings and verify the hosted purchase/refund/reconciliation flow.
6. **Exercise the full staging journey.** Check signup and email verification, login/logout/password recovery, payment success/failure/webhook retries, entitlement grants, expired/revoked access, refund/chargeback handling, lesson release, persisted progress, protected media and mobile rendering. Use test payment credentials first.
7. **Check operational tasks.** Decide how scheduled jobs/reconciliation run, confirm database/media backups, create an initial staff account through the host's secure console, and verify logs/error handling without exposing personal or payment data.

## Local checks

Run from this directory, using environment values appropriate to a local test environment:

~~~bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py check
python -m compileall -q apps config
pytest
~~~

**Latest verified CI checkpoint:** on feature checkpoint `46f67d45f4a21e817758e5e99510488ef6e02610`, the backend checks passed on Python 3.11 and 3.12; the Support & Resistance browser smoke test and integration-target guard also passed. The regression suite covers the learner dashboard, paid/expired lesson access, progress persistence, course checkout handoff, verified-payment fulfilment, repeated confirmation, failed-payment denial, refund/revocation and separately timed course-bundled community access. Refer to PR #4's workflow summaries for the exact per-runtime test counts. This is code-level verification only: no production/staging deployment, database seeding with `--apply`, or complete hosted checkout-to-lesson journey has been verified. A local check or static preview does not prove deployment readiness.
