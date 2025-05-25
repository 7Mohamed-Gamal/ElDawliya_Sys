#!/usr/bin/env python3
"""
سكريبت إعداد API نظام الدولية
ElDawliya System API Setup Script

يقوم هذا السكريبت بإعداد API بشكل كامل:
This script sets up the API completely:
1. Run migrations
2. Create user groups
3. Create superuser (optional)
4. Create API key for superuser
5. Test API endpoints
"""

import os
import sys
import django
import secrets
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from django.core.management import execute_from_command_line, call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from api.models import APIKey

User = get_user_model()


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step: str):
    """Print a step"""
    print(f"\n🔄 {step}...")


def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")


def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {message}")


def run_migrations():
    """Run database migrations"""
    print_step("Running database migrations")
    try:
        call_command('makemigrations', 'api', verbosity=0)
        call_command('migrate', verbosity=0)
        print_success("Database migrations completed")
    except Exception as e:
        print_error(f"Migration failed: {e}")
        return False
    return True


def setup_groups():
    """Setup user groups and permissions"""
    print_step("Setting up user groups and permissions")
    try:
        call_command('setup_api_groups', verbosity=0)
        print_success("User groups and permissions setup completed")
    except Exception as e:
        print_error(f"Groups setup failed: {e}")
        return False
    return True


def create_superuser():
    """Create superuser if it doesn't exist"""
    print_step("Checking for superuser")
    
    if User.objects.filter(is_superuser=True).exists():
        superuser = User.objects.filter(is_superuser=True).first()
        print_success(f"Superuser already exists: {superuser.username}")
        return superuser
    
    print_info("No superuser found. Creating one...")
    username = input("Enter superuser username (default: admin): ").strip() or "admin"
    email = input("Enter superuser email (default: admin@eldawliya.com): ").strip() or "admin@eldawliya.com"
    
    try:
        superuser = User.objects.create_superuser(
            username=username,
            email=email,
            password='admin123'  # Default password
        )
        print_success(f"Superuser created: {username}")
        print_info("Default password: admin123 (Please change it!)")
        return superuser
    except Exception as e:
        print_error(f"Failed to create superuser: {e}")
        return None


def create_api_key(user):
    """Create API key for user"""
    print_step(f"Creating API key for {user.username}")
    
    # Check if user already has an API key
    existing_key = APIKey.objects.filter(user=user, is_active=True).first()
    if existing_key:
        print_success(f"API key already exists: {existing_key.key[:8]}...{existing_key.key[-8:]}")
        return existing_key.key
    
    try:
        api_key = secrets.token_urlsafe(32)
        api_key_obj = APIKey.objects.create(
            user=user,
            name=f"Default API Key for {user.username}",
            key=api_key
        )
        print_success(f"API key created: {api_key}")
        return api_key
    except Exception as e:
        print_error(f"Failed to create API key: {e}")
        return None


def add_user_to_groups(user):
    """Add user to all API groups"""
    print_step(f"Adding {user.username} to API groups")
    
    group_names = ['API_Users', 'HR_Users', 'Inventory_Users', 'Meeting_Users', 'AI_Users']
    
    for group_name in group_names:
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            print_success(f"Added to group: {group_name}")
        except Group.DoesNotExist:
            print_error(f"Group not found: {group_name}")
    
    user.save()


def test_api():
    """Test API endpoints"""
    print_step("Testing API endpoints")
    
    try:
        import requests
        
        base_url = "http://localhost:8000/api/v1"
        
        # Test status endpoint (no auth required)
        response = requests.get(f"{base_url}/status/", timeout=5)
        if response.status_code == 200:
            print_success("API status endpoint working")
        else:
            print_error(f"API status endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print_info("Django server is not running. Start it with: python manage.py runserver")
    except ImportError:
        print_info("requests library not installed. Install with: pip install requests")
    except Exception as e:
        print_error(f"API test failed: {e}")


def create_env_file(api_key):
    """Create .env file with API configuration"""
    print_step("Creating .env file")
    
    env_content = f"""# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ACTIVE_DB=default

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-flash

# API Configuration
API_RATE_LIMIT=100
API_THROTTLE_ANON=10
API_THROTTLE_USER=60

# Example API Key (for testing)
API_KEY={api_key}

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print_success(".env file created")
        print_info("Please update GEMINI_API_KEY with your actual Gemini API key")
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")


def main():
    """Main setup function"""
    print_header("ElDawliya System API Setup")
    print("This script will set up the API completely.")
    print("Make sure you have:")
    print("1. Installed all requirements: pip install -r requirements.txt")
    print("2. Configured your database settings")
    
    proceed = input("\nProceed with setup? (y/N): ").strip().lower()
    if proceed != 'y':
        print("Setup cancelled.")
        return
    
    # Step 1: Run migrations
    if not run_migrations():
        print_error("Setup failed at migrations step")
        return
    
    # Step 2: Setup groups
    if not setup_groups():
        print_error("Setup failed at groups step")
        return
    
    # Step 3: Create superuser
    superuser = create_superuser()
    if not superuser:
        print_error("Setup failed at superuser creation step")
        return
    
    # Step 4: Add user to groups
    add_user_to_groups(superuser)
    
    # Step 5: Create API key
    api_key = create_api_key(superuser)
    if not api_key:
        print_error("Setup failed at API key creation step")
        return
    
    # Step 6: Create .env file
    create_env_file(api_key)
    
    # Step 7: Test API
    test_api()
    
    # Final instructions
    print_header("Setup Complete!")
    print("🎉 API setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Visit API documentation: http://localhost:8000/api/v1/docs/")
    print("3. Test API with the provided examples: python api_examples.py")
    print(f"4. Your API key: {api_key}")
    print("\nImportant:")
    print("- Update .env file with your Gemini API key")
    print("- Change the default superuser password")
    print("- Review security settings before production")


if __name__ == "__main__":
    main()
