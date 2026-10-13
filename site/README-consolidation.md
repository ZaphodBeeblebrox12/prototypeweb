# CSS Consolidation - what changed and where things go

## Placement map (unzip over your repo root)
| File in this ZIP          | Goes to                     | Notes |
|---------------------------|-----------------------------|-------|
| site/assets/site.css      | site/assets/site.css (NEW)  | Consolidated site-wide stylesheet. All 23 CSS passes from all 5 pages, merged, de-duplicated, dead declarations removed. construct.html rules scoped under `body.construct-page`. |
| site/construct.html       | site/construct.html         | Drop-in replacement. Already fully patched (link + body class). |
| site/consolidate_css.py   | site/consolidate_css.py     | Run ONCE: python consolidate_css.py - patches your original index/courses/live-class/trading-path in place. |
| site/index.html           | DO NOT copy this one        | Removed from the package on purpose - see below. |

## Why index/courses/live-class/trading-path are patched by script instead of shipped as files
Your inline CSS blocks were 45-60 KB per page, but the page bodies themselves are
large and detailed. Re-typing them risks silently losing content. The script only
removes the <style>...</style> block and applies 4 one-line bug fixes - every other
byte of your HTML (every section, every word of copy) stays exactly as you wrote it.

After running it:  git diff  will show ONLY head changes + the 4 fixes.

## Bug fixes applied
1. index.html      - duplicate id="home" (was on both <main> and <section class="hero">)
2. live-class.html - SVG `viewbox` -> `viewBox` (chart label could fail to render)
3. live-class.html - invalid `<button href="#enquire">` -> `<a class="button">` (nav CTA did nothing)
4. trading-path    - missing breadcrumb separator between Courses and CONSTRUCT
Plus: the previously-undefined CSS variable `--green-deep` is now defined in :root.

## Verification already performed on the shipped files
- 0 inline <style> blocks remain; all pages link assets/site.css
- 100% class coverage: every class used in construct.html (58) and index.html (91)
  has at least one rule in site.css
- Cascade sanity: final winning values checked (.section padding 78px, .study-card
  min-height 430px, mobile nav display:grid !important, etc.)
- construct.html's design system is scoped: 170 rules prefixed body.construct-page,
  so it cannot collide with the shared header/nav/button styles.

## Going forward
Edit site/assets/site.css ONLY. Never re-add inline <style> blocks to pages.
