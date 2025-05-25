#!/usr/bin/env python3
"""
بدء سريع لنظام الدولية
ElDawliya System Quick Start

يقوم هذا السكريبت بإعداد وتشغيل النظام بشكل كامل
This script sets up and runs the system completely
"""

import os
import sys
import subprocess
import time
from pathlib import Path

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

def run_command(command: list, description: str, timeout: int = 300):
    """Run a command with timeout"""
    print_step(description)
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print_success(f"{description} completed")
            return True
        else:
            print_error(f"{description} failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print_error(f"{description} timed out")
        return False
    except Exception as e:
        print_error(f"{description} failed: {e}")
        return False

def check_requirements():
    """Check if requirements are installed"""
    print_step("Checking requirements")
    
    required_packages = ['django', 'rest_framework']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print_error(f"Missing packages: {', '.join(missing_packages)}")
        print_info("Run: python install_requirements.py")
        return False
    
    print_success("Requirements check passed")
    return True

def setup_database():
    """Setup database"""
    print_step("Setting up database")
    
    # Make migrations
    if not run_command([sys.executable, 'manage.py', 'makemigrations'], "Making migrations"):
        return False
    
    # Run migrations
    if not run_command([sys.executable, 'manage.py', 'migrate'], "Running migrations"):
        return False
    
    return True

def setup_api():
    """Setup API"""
    print_step("Setting up API")
    
    # Check if setup_api.py exists
    if not Path('setup_api.py').exists():
        print_error("setup_api.py not found")
        return False
    
    # Run API setup
    return run_command([sys.executable, 'setup_api.py'], "Setting up API", timeout=600)

def create_superuser():
    """Create superuser if needed"""
    print_step("Checking for superuser")
    
    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
        import django
        django.setup()
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if User.objects.filter(is_superuser=True).exists():
            print_success("Superuser already exists")
            return True
        
        print_info("Creating default superuser...")
        user = User.objects.create_superuser(
            username='admin',
            email='admin@eldawliya.com',
            password='admin123'
        )
        print_success("Superuser created: admin / admin123")
        print_info("Please change the password after first login!")
        return True
        
    except Exception as e:
        print_error(f"Failed to create superuser: {e}")
        return False

def start_server():
    """Start Django server"""
    print_step("Starting Django server")
    
    print_success("Server starting...")
    print("\n📍 Available URLs:")
    print("   Main Application: http://localhost:8000/")
    print("   Admin Panel: http://localhost:8000/admin/")
    print("   API Documentation: http://localhost:8000/api/v1/docs/")
    print("   API Status: http://localhost:8000/api/v1/status/")
    
    print("\n🔑 Default Login:")
    print("   Username: admin")
    print("   Password: admin123")
    
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start server
        subprocess.run([sys.executable, 'manage.py', 'runserver'])
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print_error(f"Server failed to start: {e}")

def main():
    """Main quick start function"""
    print_header("ElDawliya System Quick Start")
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print_error("manage.py not found. Please run this script from the project root directory.")
        return
    
    print("🚀 This script will:")
    print("1. Check requirements")
    print("2. Setup database")
    print("3. Setup API")
    print("4. Create superuser")
    print("5. Start the server")
    
    proceed = input("\nProceed with quick start? (Y/n): ").strip().lower()
    if proceed and proceed != 'y':
        print("Quick start cancelled.")
        return
    
    # Step 1: Check requirements
    if not check_requirements():
        print_info("Install requirements first: python install_requirements.py")
        return
    
    # Step 2: Setup database
    if not setup_database():
        print_error("Database setup failed")
        return
    
    # Step 3: Setup API (optional)
    if Path('setup_api.py').exists():
        setup_api()
    else:
        print_info("API setup script not found, skipping...")
    
    # Step 4: Create superuser
    create_superuser()
    
    # Step 5: Start server
    start_server()

if __name__ == "__main__":
    main()
