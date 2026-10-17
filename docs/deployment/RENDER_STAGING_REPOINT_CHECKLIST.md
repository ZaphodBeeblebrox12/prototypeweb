# Render staging branch repoint — handoff checklist

**Status: pending dashboard changes.** The repository consolidation is committed and verified, but the live Render service settings have not been changed.

## Intended staging configuration

### Public website staging

- Service: `tradethesis-public-staging`
- Service ID: `srv-db9j72m1egvs73ffpfkg`
- Dashboard: https://dashboard.render.com/static/srv-db9j72m1egvs73ffpfkg
- Repository: `ZaphodBeeblebrox12/prototypeweb`
- Current branch (last inspected): `feature/tradethesis-academy`
- Current auto-deploy: off
- Publish path: `./site`
- Desired branch: `my-new-branch`
- Desired auto-deploy: on commit

### Django Academy staging

- Service: `tradethesis-academy-staging`
- Service ID: `srv-db9ioke1egvs73feb8ag`
- Dashboard: https://dashboard.render.com/web/srv-db9ioke1egvs73feb8ag
- Repository: `ZaphodBeeblebrox12/prototypeweb`
- Current branch (last inspected): `feature/tradethesis-academy`
- Current auto-deploy: off
- Plan: Free
- Root directory: repository root (empty)
- Build command: `cd backend && bash build.sh`
- Start command: `cd backend && gunicorn config.wsgi:application --workers 2 --threads 4 --timeout 120`
- Health check: `/health/`
- Desired branch: `my-new-branch`
- Desired auto-deploy: on commit

## Existing application to leave unchanged

- Service: `tradeadmin`
- Service ID: `srv-darvg4navr4c738cmtl0`
- Dashboard: https://dashboard.render.com/web/srv-darvg4navr4c738cmtl0
- Repository/branch: `ZaphodBeeblebrox12/test` / `main`
- Auto-deploy: on

Do not repoint or redeploy this service as part of staging consolidation.

## Operator steps

1. Open the Public website staging service and select `my-new-branch` as the deployed branch. Enable auto-deploy on commit; retain publish path `./site`.
2. Open Django Academy staging and select `my-new-branch`. Enable auto-deploy on commit; retain the repository-root root directory and the build/start commands listed above.
3. Before the first deploy, confirm the Academy service still has its required database URL and application environment variables. Do not print secret values in logs or notes.
4. Confirm the resulting deploy is built from the then-current `prototypeweb/my-new-branch` head, health check passes, and admin login works.
5. Test an admin image upload, publish/preview, protected media retrieval, and entitlement denial before considering uploaded media production-safe.

## Important limitations

The repository now contains the Django runtime under `backend/`, including the GeoLite database and its source tests. The staging Academy service remains on Render Free; course image uploads stored on its local filesystem are not durable across restarts/redeploys. Resolve private-media persistence separately (object storage or an appropriate persistent hosting setup).

The connected Render integration used for this checkpoint exposes service inspection but not an operation to edit an existing service's repository branch or auto-deploy setting. Therefore the settings above are the verified handoff target, not a claim that Render has already been reconfigured.
