# Package Separation Audit — TradeThesis Support & Resistance

**Build:** learner-safe preview v1 / internal production pack v1.7
**Scope:** static ZIP content audit only; does not verify actual server-side access controls.

## Learner-safe preview allowlist
The learner ZIP contains student orientation, course map, workbook, learner activity pack, Lesson 1–17 formative checks, the separately extracted student copy of Lesson 18's seven-item knowledge check, a chart catalogue, and curated PNG first-view charts.

## Exclusions checked
- Internal answer key, feedback bank, scoring rubric rationale and production scripts
- Annotated reference chart images and `*-reference*` chart states
- Raw OHLC data CSVs and editable SVG sources
- Internal asset IDs, production manifest and second-pass register
- Lesson 18 parallel retry chart and both internal reference-answer states
- Authentic instructor trade/chart records

## Important limitations
- Lessons 9, 16 and 17 still have instructor-material dependencies. This is a preview, not a full course release.
- Staged reveal behaviour is not delivered in a ZIP; the live system must serve the appropriate stage only after the learner's action.
- The static package audit does not prove that a future website, LMS, CDN or API keeps private payloads inaccessible. Test those systems separately.

## Second-pass items
- **SP-32:** verify package boundaries and the included chart allowlist against the final approved curriculum.
- **SP-33:** test actual deployment/access controls and inspect network/client payloads for answer keys, future charts and internal data.
- **REL-39:** student-safe package passes content and asset allowlist review.
- **REL-40:** deployed learner experience passes access-control/reveal-gating tests.