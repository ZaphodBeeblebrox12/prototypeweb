# TradeThesis public-site SEO build

The public website is a static Render site. Its SEO metadata and sitemap are
generated at build time so canonical URLs are present in the HTML source.

## Local or staging build

The defaults are the current Render staging addresses with indexing disabled:

```bash
node tools/seo/test_public_site.cjs
node tools/seo/build_public_site.cjs
```

The build processes HTML under `site/`, writes canonical, Open Graph and Twitter
metadata when indexing is explicitly enabled, emits Organization/WebSite/Course
structured data, generates `robots.txt` and `sitemap.xml`, and marks internal
review/demo pages `noindex, nofollow`.

## Render static-site build command

For `tradethesis-public-staging`, set the build command to:

```bash
node tools/seo/build_public_site.cjs
```

Keep these staging environment variables:

- `TRADETHESIS_PUBLIC_BASE_URL=https://tradethesis-public-staging.onrender.com`
- `TRADETHESIS_ACADEMY_BASE_URL=https://tradethesis-academy-staging.onrender.com`
- `TRADETHESIS_SEO_INDEXABLE=false`

The publish directory remains `site`. Do not trigger a deployment just to apply
SEO settings before the code has been reviewed.

## When a permanent domain is purchased

Set both URLs to the final HTTPS addresses and only then enable indexing:

- `TRADETHESIS_PUBLIC_BASE_URL=https://<your-public-domain>`
- `TRADETHESIS_ACADEMY_BASE_URL=https://<your-academy-host>`
- `TRADETHESIS_SEO_INDEXABLE=true`

The builder refuses to index localhost and Render `.onrender.com` hosts. This
prevents staging from accidentally becoming the canonical search property.

For the Django Academy service, set `TRADETHESIS_PUBLIC_SITE_URL` to the final
public website URL and `TRADETHESIS_SEO_INDEXABLE=true`. Its robots and sitemap
endpoints then expose only published, visible course overview pages. Lesson
bodies, member pages, admin previews and private content stay non-indexable.
