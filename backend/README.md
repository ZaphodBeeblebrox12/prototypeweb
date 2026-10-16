# TradeThesis Django backend

This directory contains the Django runtime imported from the preserved upstream source branch ZaphodBeeblebrox12/test / feature/tradethesis-academy. The product repository's integration branch is based on prototypeweb/my-new-branch; the only intended merge target is my-new-branch, never main.

## Local commands

Run commands from this directory so Django's BASE_DIR, templates, static assets and project configuration resolve relative to the backend project root:

~~~bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py check
~~~

Supply environment configuration through your deployment environment or an ignored local .env file. Secrets, database files and the GeoLite2 MMDB binary are intentionally not copied from the upstream repository. Configure GeoIP fallback/availability as documented in the upstream code before enabling geo-pricing in production.

This import does not itself connect the static member-area preview to live login, checkout, lesson delivery or persisted progress. That integration still requires route/deployment configuration and an end-to-end test run. Do not treat a static preview, a passing syntax check or an unconfigured local environment as proof of production readiness.
