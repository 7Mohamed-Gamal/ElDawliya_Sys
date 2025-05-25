from django.core.management.base import BaseCommand
from api.models import AIProvider

class Command(BaseCommand):
    help = 'Sets up default AI providers'

    def handle(self, *args, **kwargs):
        # Check if Gemini provider exists
        gemini_exists = AIProvider.objects.filter(name='gemini').exists()
        if not gemini_exists:
            self.stdout.write('Creating Gemini provider...')
            AIProvider.objects.create(
                name='gemini',
                display_name='Google Gemini',
                description='Google Gemini models provide advanced AI capabilities.',
                is_active=True,
                requires_api_key=True
            )
            self.stdout.write(self.style.SUCCESS('Successfully created Gemini provider'))
        else:
            self.stdout.write('Gemini provider already exists')
        
        # Check if OpenAI provider exists
        openai_exists = AIProvider.objects.filter(name='openai').exists()
        if not openai_exists:
            self.stdout.write('Creating OpenAI provider...')
            AIProvider.objects.create(
                name='openai',
                display_name='OpenAI GPT',
                description='OpenAI GPT models for advanced language AI.',
                is_active=True,
                requires_api_key=True
            )
            self.stdout.write(self.style.SUCCESS('Successfully created OpenAI provider'))
        else:
            self.stdout.write('OpenAI provider already exists')
        
        # Display all providers
        providers = AIProvider.objects.all()
        self.stdout.write('\nCurrent AI Providers:')
        for provider in providers:
            self.stdout.write(f'- {provider.name} ({provider.display_name}): {"Active" if provider.is_active else "Inactive"}')
