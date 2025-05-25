"""
Script to test GeminiService functionality directly
"""
import os
import sys
import django
import logging

# Set up logging
logging.basicConfig(
    filename='debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set up Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

# Import models and services after Django setup
from django.contrib.auth import get_user_model
from api.models import AIProvider, AIConfiguration
from api.services import GeminiService

User = get_user_model()

def create_test_data():
    """Create test data for GeminiService testing"""
    print("Creating test data...")
    logging.info("Creating test data...")
    
    # Create Gemini provider if it doesn't exist
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
        print(f"Created provider: {provider.name}")
    else:
        print(f"Provider already exists: {provider.name}")
    
    # Get or create a test user
    username = 'testadmin'
    try:
        user = User.objects.get(username=username)
        print(f"Using existing user: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email='test@example.com',
            password='password123',
            is_staff=True,
            is_superuser=True
        )
        print(f"Created test user: {username}")
    
    # Create API configuration for the test user
    # Add your real Gemini API key here for testing
    api_key = os.getenv('GEMINI_API_KEY', 'your_api_key_here')
    
    config, created = AIConfiguration.objects.get_or_create(
        user=user,
        provider=provider,
        defaults={
            'api_key': api_key,
            'model_name': 'gemini-1.5-flash',
            'is_default': True,
            'is_active': True,
            'max_tokens': 1000,
            'temperature': 0.7
        }
    )
    
    if created:
        print(f"Created API config for user {user.username}: {config.id}")
    else:
        # Update the API key if it has changed
        if config.api_key != api_key:
            config.api_key = api_key
            config.save()
            print(f"Updated API key for config {config.id}")
        else:
            print(f"API config already exists for user {user.username}: {config.id}")
    
    # Display all configurations
    configs = AIConfiguration.objects.filter(user=user)
    print("\nUser API Configurations:")
    for cfg in configs:
        print(f"- ID: {cfg.id}, Provider: {cfg.provider.name}, Active: {cfg.is_active}, Default: {cfg.is_default}")
    
    return user

def test_gemini_service(user):
    """Test GeminiService functionality"""
    print("\nTesting GeminiService...")
    logging.info("Testing GeminiService...")
    
    # Initialize GeminiService
    service = GeminiService(user=user)
    logging.info(f"Initialized GeminiService for user {user.username}")
    
    # Get service configuration info
    print(f"Service is_configured: {service.is_configured}")
    print(f"Service API key exists: {bool(service.api_key)}")
    print(f"Service model: {service.model_name}")
    print(f"Service config source: {service.config_source}")
    
    if not service.is_configured:
        print("\nERROR: Service is not configured!")
        missing = []
        if not service.api_key:
            missing.append("API key")
        import google.generativeai as genai
        if 'genai' not in globals():
            missing.append("genai library")
        print(f"Missing: {', '.join(missing) or 'unknown issue'}")
        return False
    
    # Test response generation
    print("\nTesting response generation...")
    test_message = "مرحباً، اختبار بسيط للتأكد من عمل الخدمة"
    result = service.generate_response(test_message)
    
    if result['success']:
        print("SUCCESS: Generated response")
        print(f"Response: {result['response'][:100]}...")
        print(f"Tokens used: {result['tokens_used']}")
        return True
    else:
        print(f"ERROR: {result.get('error', 'Unknown error')}")
        if 'traceback' in result:
            print(f"Traceback: {result['traceback']}")
        return False

if __name__ == "__main__":
    user = create_test_data()
    success = test_gemini_service(user)
    
    if success:
        print("\nThe GeminiService test was successful!")
    else:
        print("\nThe GeminiService test failed!")
