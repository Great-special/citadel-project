import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import StaticContentBlock
from core.static_content import clear_static_content_cache


class Command(BaseCommand):
    help = 'Import static page translations from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to the CSV file to import.')

    @transaction.atomic
    def handle(self, *args, **options):
        csv_path = options['csv_path']

        try:
            with open(csv_path, newline='', encoding='utf-8-sig') as csv_file:
                reader = csv.DictReader(csv_file)
                required_columns = {'en', 'de'}
                if not reader.fieldnames or not required_columns.issubset(reader.fieldnames):
                    raise CommandError(
                        "CSV must include 'en' and 'de' columns, plus either 'key' or both 'page' and 'block'."
                    )

                imported = 0
                for row_number, row in enumerate(reader, start=2):
                    page = (row.get('page') or '').strip()
                    block = (row.get('block') or '').strip()
                    key = (row.get('key') or '').strip()

                    if key and (not page or not block):
                        page, separator, block = key.partition('.')
                        if not separator or not page or not block:
                            raise CommandError(
                                f"Row {row_number}: key '{key}' must use the format 'page.block'."
                            )

                    if not page or not block:
                        raise CommandError(
                            f"Row {row_number}: provide either 'key' or both 'page' and 'block'."
                        )

                    is_rich_text = str(row.get('is_rich_text', '')).strip().lower() in {
                        '1',
                        'true',
                        'yes',
                    }

                    StaticContentBlock.objects.update_or_create(
                        page=page,
                        block=block,
                        defaults={
                            'content_en': row.get('en', ''),
                            'content_de': row.get('de', ''),
                            'is_rich_text': is_rich_text,
                        },
                    )
                    imported += 1
        except FileNotFoundError as exc:
            raise CommandError(f"CSV file not found: {csv_path}") from exc

        clear_static_content_cache()
        self.stdout.write(self.style.SUCCESS(f'Imported {imported} static content blocks.'))
