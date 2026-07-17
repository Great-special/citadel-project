from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent
FACULTY_TEMPLATE = ROOT / "core" / "templates" / "faculty.html"


class FacultyMobileRegressionTests(unittest.TestCase):
    def test_faculty_template_has_mobile_card_grid_override(self):
        faculty_html = FACULTY_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("@media (max-width: 768px)", faculty_html)
        self.assertIn(".fac-grid { grid-template-columns: 1fr; }", faculty_html)
        self.assertIn(".fac-card { padding: 28px 22px; }", faculty_html)

    def test_faculty_template_has_mobile_footer_override(self):
        faculty_html = FACULTY_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn(".footer-grid { grid-template-columns: 1fr; gap: 32px; }", faculty_html)
        self.assertIn(".footer-bottom { flex-direction: column; align-items: flex-start; }", faculty_html)

    def test_faculty_template_scales_bio_overlay_text_for_phone(self):
        faculty_html = FACULTY_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("@media (max-width: 480px)", faculty_html)
        self.assertIn(".display-serif { font-size: 2rem; }", faculty_html)
        self.assertIn(".proof-item { padding: 20px 18px 18px; min-height: auto; }", faculty_html)


if __name__ == "__main__":
    unittest.main()
