# yourapp/management/commands/auto_translate.py

from django.core.management.base import BaseCommand
from deep_translator import GoogleTranslator
import polib
import os
from django.conf import settings
from time import sleep

class Command(BaseCommand):
    help = 'Automatically translate PO files using free translation API'

    def add_arguments(self, parser):
        parser.add_argument('--language', type=str, help='Target language code (e.g., es, fr)')

    def translate_text(self, text, translator):
        """Helper function to handle translation with error checking"""
        try:
            if not text or text.strip() == '':
                return ''
                
            translated = translator.translate(text)
            return translated if translated else ''
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Translation error: {str(e)}'))
            return ''

    def handle(self, *args, **options):
        language = options['language']
        
        # Ensure language is provided
        if not language:
            self.stdout.write(self.style.ERROR('Please provide a language code'))
            return

        locale_path = os.path.join(settings.BASE_DIR, 'locale', language, 'LC_MESSAGES', 'django.po')

        if not os.path.exists(locale_path):
            self.stdout.write(self.style.ERROR(f'PO file for language {language} not found at {locale_path}'))
            return

        try:
            # Load the PO file
            po = polib.pofile(locale_path)
            untranslated = po.untranslated_entries()
            total = len(untranslated)
            
            if total == 0:
                self.stdout.write(self.style.SUCCESS('No untranslated messages found!'))
                return
                
            self.stdout.write(f'Found {total} untranslated messages')

            # Initialize translator
            translator = GoogleTranslator(source='en', target=language)

            # Translate each untranslated entry
            for i, entry in enumerate(untranslated, 1):
                try:
                    # Skip empty messages
                    if not entry.msgid or entry.msgid.strip() == '':
                        continue

                    # Add a small delay to avoid rate limiting
                    sleep(1)

                    # Get translation with error handling
                    translated_text = self.translate_text(entry.msgid, translator)
                    
                    if translated_text:
                        entry.msgstr = translated_text
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'[{i}/{total}] Translated: {entry.msgid} → {entry.msgstr}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'[{i}/{total}] Skipped: {entry.msgid}'
                            )
                        )
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing entry {entry.msgid}: {str(e)}')
                    )
                    # Wait longer if we hit an error (might be rate limiting)
                    sleep(5)
                    continue

            # Save the translated PO file
            try:
                po.save()
                self.stdout.write(self.style.SUCCESS('Translations saved successfully!'))
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error saving translations: {str(e)}')
                )
                return

            # Compile the messages
            try:
                self.stdout.write('Compiling messages...')
                os.system(f'python manage.py compilemessages')
                self.stdout.write(self.style.SUCCESS('Messages compiled successfully!'))
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error compiling messages: {str(e)}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'An unexpected error occurred: {str(e)}')
            )