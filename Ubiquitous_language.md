# Ubiquitous Language

- `Base shell`: The shared page frame in `core/templates/base.html` that provides the nav, footer, theme toggle, and script includes for most public pages.
- `Language-prefixed route`: A public page URL with a locale segment such as `/de/contact/`. English stays on the default unprefixed route.
- `Static content block`: A database-backed copy entry keyed by `page.block`, for example `contact.hero.eyebrow` or `base.nav.group`.
- `English fallback`: The rule that serves `content_en` whenever a German value is missing or blank.
- `Rich text block`: A static content block whose stored value may include HTML markup and is rendered as page content.
- `Translation seed CSV`: The development-time document imported by `python manage.py import_static_translations <path>`, used to create or update static content blocks.
- `Desktop nav`: The inline navigation inside `.nav-links`, shown on larger screens.
- `Mobile drawer`: The collapsible menu inside `#mobMenu`, opened by the hamburger on smaller screens.
- `Mobile link`: A button with the `.mob-link` class. These links are styled for stacked, full-width navigation inside the mobile drawer.
- `Shared stylesheet`: `core/static/css/style.css`, the CSS file that controls responsive behavior for pages extending the base shell.
- `Working reference`: `core/templates/akademie.html`, the page whose mobile nav behavior is currently considered correct and safe to mirror.
- `Responsive breakpoint`: A viewport width where layout rules change, especially for the nav and footer.
