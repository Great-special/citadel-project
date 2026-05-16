from django.core.management.base import BaseCommand
from django.apps import apps
from deep_translator import GoogleTranslator
from time import sleep
from django.conf import settings
from django.db import transaction

class Command(BaseCommand):
    help = 'Automatically translate all translatable fields in a Django app using free translation API'

    def add_arguments(self, parser):
        parser.add_argument('--language', type=str, help='Target language code (e.g., es, fr)')
        parser.add_argument('--app', type=str, help='App name to auto-translate')

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

    @transaction.atomic
    def translate_model_fields(self, model, translatable_fields, translator, language):
        """Translate fields for all instances of the given model"""
        instances = model.objects.all()
        total = len(instances)

        self.stdout.write(f'Translating {total} instances of model {model.__name__}...')
        
        for i, instance in enumerate(instances, 1):
            updated = False
            for field in translatable_fields:
                original_text = getattr(instance, field, None)
                if not original_text or original_text.strip() == '':
                    continue

                # Get translation with error handling
                translated_text = self.translate_text(original_text, translator)
                
                if translated_text:
                    # Set the translated field (e.g., field + "_fr" for French)
                    translated_field = f"{field}_{language}"
                    setattr(instance, translated_field, translated_text)
                    updated = True
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'[{i}/{total}] Translated {field}: {original_text} → {translated_text}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'[{i}/{total}] Skipped {field}: {original_text}'
                        )
                    )
            
            if updated:
                instance.save()

    def handle(self, *args, **options):
        language = options['language']
        app_name = options['app']
        
        # Ensure both language and app name are provided
        if not language:
            self.stdout.write(self.style.ERROR('Please provide a target language code using --language'))
            return
        
        if not app_name:
            self.stdout.write(self.style.ERROR('Please provide an app name using --app'))
            return

        # Validate language code
        if language not in settings.MODELTRANSLATION_LANGUAGES:
            self.stdout.write(self.style.ERROR(f'Invalid language code: {language}'))
            return

        try:
            # Initialize translator
            translator = GoogleTranslator(source='en', target=language)

            # Get app models
            app_config = apps.get_app_config(app_name)
            for model in app_config.get_models():
                # Identify translatable fields using Django-modeltranslation's convention
                translatable_fields = [
                    field.name for field in model._meta.get_fields()
                    if hasattr(model, f'{field.name}_{language}')
                ]

                if not translatable_fields:
                    self.stdout.write(
                        self.style.WARNING(f'No translatable fields found for model {model.__name__}')
                    )
                    continue

                # Translate fields for the model
                self.translate_model_fields(model, translatable_fields, translator, language)

            self.stdout.write(self.style.SUCCESS('Auto-translation completed successfully!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An unexpected error occurred: {str(e)}'))
