# Public programme enquiry workflow — staging and release setup

This workflow collects anonymous prospect enquiries for CONSTRUCT and the six-week Live Classroom. It is deliberately separate from authenticated member support tickets.

## Required deployment configuration

1. Apply Django migrations, including `support.0009_course_enquiries`.
2. Configure the exact public website origin(s) in the Academy service:
   - `TRADETHESIS_PUBLIC_SITE_ORIGINS=https://your-public-site-host`
   - Keep `TRADETHESIS_PUBLIC_SITE_URL` set to the public website's canonical origin as used by the existing account and email flows.
   - The default allowlist also includes the repository GitHub Pages preview origin `https://zaphodbeeblebrox12.github.io` (the `/prototypeweb/` path is not part of the origin). Override the list explicitly when the public host changes; include only origins that genuinely serve the TradeThesis forms.
   - Do not use wildcards or include unrelated origins. For multiple approved public hosts, supply a comma-separated list.
3. Ensure the public website injects the correct `TRADETHESIS_ACADEMY_BASE_URL` before `site/assets/academy-config.js` runs. The staging host mapping already exists; unknown production hosts intentionally remain disabled until explicitly configured.
4. Configure the existing transactional email backend, `DEFAULT_FROM_EMAIL`, and the provider credentials required by that backend. The enquiry itself is saved even if an email attempt fails; receipt status is recorded on the enquiry.
5. Grant the sales/reviewer group these Django model permissions:
   - `support.view_courseenquiry` to open the queue and read enquiry records.
   - `support.change_courseenquiry` to assign records, add private notes, change status and send replies.
   
   Do not grant these permissions to every staff member by default. Superusers retain Django's normal implicit permissions.

## Behaviour and safeguards

- The public pages submit ordinary urlencoded POST forms to `/public/enquiries/` on the configured Academy origin.
- The endpoint accepts only POST and checks the exact browser Origin (or Referer fallback) against `TRADETHESIS_PUBLIC_SITE_ORIGINS`. It does not use or mutate a logged-in customer's session, which is why the cross-origin public form uses this narrow origin boundary rather than a CSRF cookie.
- Name, email, programme, starting-point choice, message length and explicit response consent are validated server-side. A hidden honeypot is ignored without creating a record.
- A single email address may submit at most two enquiries for the same programme in a rolling hour. This is a light anti-abuse measure, not a substitute for CAPTCHA or WAF protection if public spam volume grows.
- No raw IP address is stored. There is no marketing opt-in; the contact details are used only to respond to the enquiry.
- Receipt and staff notification emails are attempted through the configured email backend. The Admin Desk record and in-app staff notification remain authoritative when email is unavailable.
- A staff reply is recorded as accepted only when Django's email backend reports that it accepted the message. This is not proof of delivery to the recipient's inbox.
- Enquiry and reply records are private staff data. The public cannot read them; member support permissions do not grant enquiry access.

## Staging acceptance

Run the backend regression tests:

```bash
cd backend
python manage.py test apps.support.test_course_enquiries
python manage.py makemigrations --check --dry-run
python manage.py check
```

Then verify manually with the public staging website and Academy staging service:

1. Submit one CONSTRUCT enquiry and one Live Classroom enquiry.
2. Confirm each returns to its own page with a received message and creates one record.
3. Confirm the configured receipt email and staff notification are accepted by the email backend; inspect the recorded email status.
4. Sign in as a staff member with view/change enquiry permissions and verify queue filtering, assignment, private notes, status changes and replies.
5. Verify a staff member without those permissions receives 403 and cannot open the contact details.
6. Try a wrong Origin, a blank-consent submission, a filled honeypot, an invalid email and a third same-email submission within one hour.
7. Test the forms at mobile width and confirm the privacy link resolves to the Academy privacy policy.

Do not describe the workflow as production-ready until these checks pass on the deployed staging pair and the production public origin has been configured.
