import csv
from decimal import Decimal
import os
import tempfile

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Category, Course, CourseRegistration, StaticContentBlock


class CourseRegistrationPageTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Track 1: Leadership Journey",
            short="Leadership Journey",
            color="#2d7038",
        )
        self.course = Course.objects.create(
            category=self.category,
            title="Leadership Spark",
            subtitle="Lead with clarity under pressure",
            description="An intensive leadership programme for senior operators.",
            price=Decimal("4500.00"),
            duration="5 days",
            level="Senior Leaders",
            training_format="Executive",
        )

    def test_registration_page_renders_with_selected_course(self):
        response = self.client.get(
            reverse("register_course"),
            {"course_id": self.course.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Course Registration")
        self.assertContains(response, self.course.title)
        self.assertContains(response, self.course.duration)
        self.assertContains(response, 'name="course_id"', html=False)

    def test_registration_page_lists_courses_when_no_course_is_selected(self):
        response = self.client.get(reverse("register_course"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.title)
        self.assertContains(response, "Choose a course")

    def test_valid_submission_creates_registration(self):
        response = self.client.post(
            reverse("register_course"),
            data={
                "course_id": self.course.id,
                "session": "June 2026 Cohort",
                "title": "Dr.",
                "name": "Amina Yusuf",
                "email": "amina@example.com",
                "designation": "Operations Manager",
                "company": "North Meridian Energy",
                "address": "12 Marina Road",
                "city": "Lagos",
                "country": "Nigeria",
                "telephone": "",
                "mobile": "+2348000000000",
                "fax": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(CourseRegistration.objects.count(), 1)

        registration = CourseRegistration.objects.get()
        self.assertEqual(registration.course, self.course)
        self.assertEqual(registration.name, "Amina Yusuf")
        self.assertEqual(
            response.url,
            f"{reverse('register_course')}?course_id={self.course.id}",
        )

    def test_invalid_submission_returns_errors_on_page(self):
        response = self.client.post(
            reverse("register_course"),
            data={
                "course_id": self.course.id,
                "session": "",
                "title": "Dr.",
                "name": "",
                "email": "not-an-email",
                "designation": "",
                "company": "",
                "address": "",
                "city": "",
                "country": "",
                "telephone": "",
                "mobile": "",
                "fax": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CourseRegistration.objects.count(), 0)
        self.assertContains(response, "Please correct the highlighted fields.")


class SharedBaseTemplateTests(TestCase):
    def test_index_mobile_menu_uses_mobile_link_styling(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="mob-menu" id="mobMenu">', html=False)
        self.assertContains(response, '<button class="mob-link" onclick="window.location.href=\'/\'">Group</button>', html=False)
        self.assertContains(response, '<button class="mob-link" onclick="window.location.href=\'/akademie/\'">Akademie</button>', html=False)
        self.assertNotContains(response, '<div class="mob-menu" id="mobMenu">\n            <button class="nav-link"', html=False)


class StaticContentBlockTests(TestCase):
    def test_value_for_german_falls_back_to_english(self):
        block = StaticContentBlock.objects.create(
            page="contact",
            block="hero.eyebrow",
            content_en="Start a Conversation",
            content_de="",
        )

        self.assertEqual(block.value_for("de"), "Start a Conversation")
        self.assertEqual(block.value_for("en"), "Start a Conversation")


class StaticContentImportCommandTests(TestCase):
    def test_import_command_creates_and_updates_blocks_from_csv(self):
        existing = StaticContentBlock.objects.create(
            page="contact",
            block="hero.eyebrow",
            content_en="Old English",
            content_de="Altes Deutsch",
        )

        with tempfile.NamedTemporaryFile(
            "w",
            newline="",
            suffix=".csv",
            delete=False,
            encoding="utf-8",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=["page", "block", "en", "de", "is_rich_text"],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "page": "contact",
                    "block": "hero.eyebrow",
                    "en": "Start a Conversation",
                    "de": "Gespräch beginnen",
                    "is_rich_text": "false",
                }
            )
            writer.writerow(
                {
                    "page": "base",
                    "block": "nav.group",
                    "en": "Group",
                    "de": "Gruppe",
                    "is_rich_text": "false",
                }
            )
            csv_path = csv_file.name

        try:
            call_command("import_static_translations", csv_path)
        finally:
            os.unlink(csv_path)

        existing.refresh_from_db()
        self.assertEqual(existing.content_en, "Start a Conversation")
        self.assertEqual(existing.content_de, "Gespräch beginnen")

        new_block = StaticContentBlock.objects.get(page="base", block="nav.group")
        self.assertEqual(new_block.content_en, "Group")
        self.assertEqual(new_block.content_de, "Gruppe")


class StaticContentRouteTests(TestCase):
    def test_german_prefixed_route_uses_translated_static_blocks(self):
        StaticContentBlock.objects.create(
            page="base",
            block="nav.group",
            content_en="Group",
            content_de="Gruppe",
        )
        StaticContentBlock.objects.create(
            page="contact",
            block="hero.eyebrow",
            content_en="Start a Conversation",
            content_de="Gespräch beginnen",
        )

        response = self.client.get("/de/contact/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gespräch beginnen")
        self.assertContains(response, "Gruppe")

    def test_german_prefixed_route_falls_back_to_english_when_translation_missing(self):
        StaticContentBlock.objects.create(
            page="contact",
            block="hero.eyebrow",
            content_en="Start a Conversation",
            content_de="",
        )

        response = self.client.get("/de/contact/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Start a Conversation")

    def test_german_prefixed_legal_pages_render(self):
        privacy_response = self.client.get("/de/privacy/")
        imprint_response = self.client.get("/de/imprint/")

        self.assertEqual(privacy_response.status_code, 200)
        self.assertEqual(imprint_response.status_code, 200)
