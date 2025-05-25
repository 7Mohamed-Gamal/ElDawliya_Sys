#!/usr/bin/env python3
"""
سكريبت تشغيل خادم API نظام الدولية
ElDawliya System API Server Runner

يقوم هذا السكريبت بتشغيل خادم Django مع إعدادات محسنة للـ API
This script runs Django server with optimized settings for API
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {message}")

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def check_requirements():
    """Check if all requirements are installed"""
    print_info("Checking requirements...")
    
    required_packages = [
        'django',
        'djangorestframework',
        'drf_yasg',
        'corsheaders',
        'rest_framework_simplejwt'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print_error(f"Missing packages: {', '.join(missing_packages)}")
        print_info("Install with: pip install -r requirements.txt")
        return False
    
    print_success("All required packages are installed")
    return True

def check_database():
    """Check database connection"""
    print_info("Checking database connection...")
    
    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
        import django
        django.setup()
        
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print_success("Database connection successful")
        return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False

def run_migrations():
    """Run database migrations if needed"""
    print_info("Checking for pending migrations...")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'showmigrations', '--plan'
        ], capture_output=True, text=True, check=True)
        
        if '[ ]' in result.stdout:
            print_info("Running pending migrations...")
            subprocess.run([
                sys.executable, 'manage.py', 'migrate'
            ], check=True)
            print_success("Migrations completed")
        else:
            print_success("No pending migrations")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Migration check failed: {e}")
        return False

def collect_static():
    """Collect static files if needed"""
    print_info("Collecting static files...")
    
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'collectstatic', '--noinput'
        ], capture_output=True, check=True)
        print_success("Static files collected")
        return True
    except subprocess.CalledProcessError as e:
        print_info("Static files collection skipped (not critical for development)")
        return True

def start_server(host='127.0.0.1', port=8000, open_browser=True):
    """Start Django development server"""
    print_info(f"Starting Django server on {host}:{port}...")
    
    # URLs to display
    urls = {
        'Admin Panel': f'http://{host}:{port}/admin/',
        'API Documentation': f'http://{host}:{port}/api/v1/docs/',
        'API ReDoc': f'http://{host}:{port}/api/v1/redoc/',
        'API Status': f'http://{host}:{port}/api/v1/status/',
        'Main Application': f'http://{host}:{port}/',
    }
    
    print_success("Server starting...")
    print("\n📍 Available URLs:")
    for name, url in urls.items():
        print(f"   {name}: {url}")
    
    print("\n🔑 API Authentication:")
    print("   - Use API Key: Authorization: ApiKey YOUR_API_KEY")
    print("   - Use JWT Token: Authorization: Bearer YOUR_JWT_TOKEN")
    print("   - Use Session Auth for web interface")
    
    print("\n📖 Quick API Examples:")
    print("   - Get API status: GET /api/v1/status/")
    print("   - List employees: GET /api/v1/employees/")
    print("   - List products: GET /api/v1/products/")
    print("   - Chat with AI: POST /api/v1/ai/chat/")
    
    print("\n🛠️ Management Commands:")
    print("   - Create API key: python manage.py create_api_key username")
    print("   - Setup groups: python manage.py setup_api_groups")
    print("   - Run tests: python manage.py test api")
    
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser
    if open_browser:
        time.sleep(2)  # Wait for server to start
        webbrowser.open(urls['API Documentation'])
    
    try:
        # Start Django server
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', f'{host}:{port}'
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print_error(f"Server failed to start: {e}")

def main():
    """Main function"""
    print_header("ElDawliya System API Server")
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print_error("manage.py not found. Please run this script from the project root directory.")
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Run ElDawliya API Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    parser.add_argument('--skip-checks', action='store_true', help='Skip pre-flight checks')
    
    args = parser.parse_args()
    
    if not args.skip_checks:
        # Pre-flight checks
        print_info("Running pre-flight checks...")
        
        if not check_requirements():
            return
        
        if not check_database():
            print_info("Database check failed, but continuing anyway...")
        
        if not run_migrations():
            print_info("Migration check failed, but continuing anyway...")
        
        collect_static()
    
    # Start server
    start_server(
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser
    )

if __name__ == "__main__":
    main()
