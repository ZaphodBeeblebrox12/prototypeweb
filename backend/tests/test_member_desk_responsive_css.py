from pathlib import Path

from django.test import SimpleTestCase


class MemberDeskResponsiveCssTests(SimpleTestCase):
    """Keep the real member dashboard's mobile breakpoints effective."""

    def test_mobile_overrides_follow_the_base_no_purchase_grid_rules(self):
        css_path = Path(__file__).resolve().parents[1] / "static" / "css" / "member-desk.css"
        css = css_path.read_text(encoding="utf-8")

        base_grid_rule = ".no-purchase-choice-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))"
        override_marker = "/* Mobile responsive overrides for the signed-in member dashboard."

        self.assertIn(base_grid_rule, css)
        self.assertIn(override_marker, css)
        self.assertGreater(css.index(override_marker), css.index(base_grid_rule))

        responsive_rules = css[css.index(override_marker):]
        self.assertIn("@media (max-width: 900px)", responsive_rules)
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr));", responsive_rules)
        self.assertIn("@media (max-width: 650px)", responsive_rules)
        self.assertIn("grid-template-columns: minmax(0, 1fr);", responsive_rules)
        self.assertIn(".no-purchase-service-row .btn", responsive_rules)
