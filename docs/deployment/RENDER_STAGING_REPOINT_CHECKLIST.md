# Render staging repoint — handoff checklist

**Status: code deployment succeeded; remaining validation is database identity and admin/course workflows.**

## Current verified deployment (2026-10-17)

### Public website staging

- Service: `tradethesis-public-staging`
- Service ID: `srv-db9j72m1egvs73ffpfkg`
- Dashboard: https://dashboard.render.com/static/srv-db9j72m1egvs73ffpfkg
- Repository: `ZaphodBeeblebrox12/prototypeweb`
- Branch: `my-new-branch`
- Live commit observed: `00821b6a62cf62334ce7e6a8952d624067c0c073`
- Publish path: `./site`
- Auto-deploy: off (manual deploy only)

### Django Academy staging

- Service: `tradethesis-academy-staging`
- Service ID: `srv-db9ioke1egvs73feb8ag`
- Dashboard: https://dashboard.render.com/web/srv-db9ioke1egvs73feb8ag
- Repository: `ZaphodBeeblebrox12/prototypeweb`
- Branch: `my-new-branch`
- Live commit: `6c1ac5c100f58dd185eb2b1e7ca9fb9bc3345bed` — `Fix production host environment list parsing`
- Deployment ID: `dep-db9qgr6q1p3s7397me30`
- Deployment status: `live`; build and deploy events succeeded.
- Build command: `cd backend && bash build.sh`
- Start command: `cd backend && gunicorn config.wsgi:application --workers 2 --threads 4 --timeout 120`
- Health check path: `/health/`
- Health verification: Render logs recorded repeated `GET /health/ HTTP/1.1` responses with status `200` after startup, including after deployment completion.
- Migrations logged as applied: `academy.0002_course_import_review_workflow` and `academy.0003_course_asset_original_url`.
- Auto-deploy: off (manual deploy only)
- Plan: Free; one instance.

## Next required checks

1. **Confirm database identity before relying on persistent data.** In the Academy service's Render Environment page, verify that `DATABASE_URL` exists and is sourced from the intended durable PostgreSQL database. Do not share or commit its value. If absent, the code falls back to SQLite under the backend directory, which is not a reliable production database on an ephemeral service.
2. The Render workspace currently lists one PostgreSQL instance, `tradeadmin-db`, on the Free plan, with expiry shown as 2026-10-26. Do not assume Academy uses it until `DATABASE_URL` is checked. A read-only query through the connected Render integration was blocked because the database IP allowlist is empty; do not weaken the allowlist just for this check.
3. Test admin login at the deployed Academy service. Do not assume a superuser exists. If necessary, use the guarded one-time bootstrap described in `backend/build.sh`; set the required variables privately, confirm the admin exists, then remove the bootstrap variables immediately.
4. Test admin editing/upload of lesson images, preview, protected-media access, and entitlement denial before treating this as production-ready.
5. Decide on durable private-media storage. Academy staging runs on Render Free and files saved on the container filesystem are not durable across restarts/redeploys. Use object storage or an appropriate persistent hosting setup while preserving private media access controls.
6. If desired, enable auto-deploy on commit for the two staging services in the Render dashboard. Both currently have auto-deploy off, so new commits need a manual deploy. The existing `tradeadmin` service must remain untouched on `ZaphodBeeblebrox12/test` / `main`.

## Existing application to leave unchanged

- Service: `tradeadmin`
- Service ID: `srv-darvg4navr4c738cmtl0`
- Dashboard: https://dashboard.render.com/web/srv-darvg4navr4c738cmtl0
- Repository/branch: `ZaphodBeeblebrox12/test` / `main`
- Auto-deploy: on

Do not repoint or redeploy this service as part of staging consolidation.

## Current deployment notes

- The static-site deployment and Academy deployment were triggered manually.
- The latest Academy build succeeded after changing `backend/config/settings/production.py` to use `env.list()` for comma-separated host/origin settings instead of calling `.split()` on the list returned by django-environ.
- No secrets were read into the checkpoint, added to Git, or printed into the logs.
