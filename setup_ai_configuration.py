"""
Script to set up AI configuration for all users in the system
To run: python setup_ai_configuration.py
"""
import os
import sys
import django
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Set up Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

# Import models after Django setup
from django.contrib.auth import get_user_model
from api.models import AIProvider, AIConfiguration

User = get_user_model()

def setup_ai_configuration():
    """Set up AI configuration for all users"""
    print("Setting up AI configuration for all users...")
    logging.info("Setting up AI configuration for all users")
    
    # Get the API key from environment
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    gemini_model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    
    if not gemini_api_key:
        print("ERROR: GEMINI_API_KEY not found in environment variables")
        return False
    
    # Get or create Gemini provider
    provider, created = AIProvider.objects.get_or_create(
        name='gemini',
        defaults={
            'display_name': 'Google Gemini',
            'description': 'Google Gemini AI models',
            'is_active': True,
            'requires_api_key': True
        }
    )
    
    if created:
        print(f"Created Gemini provider: {provider.name}")
    else:
        print(f"Using existing provider: {provider.name}")
    
    # Get all users
    users = User.objects.all()
    print(f"Found {users.count()} users")
    
    for user in users:
        # Check if configuration already exists
        config = AIConfiguration.objects.filter(
            user=user,
            provider=provider
        ).first()
        
        if config:
            # Update existing configuration
            config.api_key = gemini_api_key
            config.model_name = gemini_model
            config.is_default = True
            config.is_active = True
            config.save()
            print(f"Updated configuration for user: {user.username}")
        else:
            # Create new configuration
            AIConfiguration.objects.create(
                user=user,
                provider=provider,
                api_key=gemini_api_key,
                model_name=gemini_model,
                is_default=True,
                is_active=True
            )
            print(f"Created configuration for user: {user.username}")
    
    print("AI configuration setup completed successfully")
    return True

if __name__ == "__main__":
    setup_ai_configuration()
