from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
BASE_TEMPLATE = ROOT / "core" / "templates" / "base.html"
STYLE_SHEET = ROOT / "core" / "static" / "css" / "style.css"


class BaseShellRegressionTests(unittest.TestCase):
    def test_mobile_drawer_uses_mobile_link_class(self):
        base_html = BASE_TEMPLATE.read_text(encoding="utf-8")
        mobile_drawer = base_html.split('<div class="mob-menu" id="mobMenu">', 1)[1].split("</div>", 1)[0]

        self.assertIn('<div class="mob-menu" id="mobMenu">', base_html)
        self.assertIn('<button class="mob-link" onclick="window.location.href=\'{% url \'index\' %}\'">{% copy_text \'base.nav.group\' \'Group\' %}</button>', mobile_drawer)
        self.assertNotIn('class="nav-link"', mobile_drawer)

    def test_base_nav_logo_matches_shared_script_hook(self):
        base_html = BASE_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn('class="nav-logo" id="navLogo"', base_html)

    def test_shared_stylesheet_has_mobile_nav_and_footer_breakpoints(self):
        css = STYLE_SHEET.read_text(encoding="utf-8")

        self.assertIn("@media (max-width: 768px)", css)
        self.assertIn(".nav-links { display: none; }", css)
        self.assertIn(".hamburger { display: flex; }", css)
        self.assertIn(".footer-grid { grid-template-columns: 1fr; gap: 32px; }", css)


if __name__ == "__main__":
    unittest.main()
