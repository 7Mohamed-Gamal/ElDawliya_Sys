#!/usr/bin/env python3
"""
تشغيل أساسي لنظام الدولية
Basic ElDawliya System Runner

يقوم بتشغيل النظام الأساسي بدون API
Runs the basic system without API
"""

import os
import sys
import subprocess

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)

def print_step(step: str):
    """Print a step"""
    print(f"\n🔄 {step}...")

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def run_command(command: list, description: str):
    """Run a command"""
    print_step(description)
    try:
        result = subprocess.run(command, check=True)
        print_success(f"{description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed: {e}")
        return False

def main():
    """Main function"""
    print_header("ElDawliya System - Basic Runner")
    
    print("🚀 Starting basic system setup...")
    print("Note: API features are disabled until dependencies are installed")
    
    # Step 1: Make migrations
    if not run_command([sys.executable, 'manage.py', 'makemigrations'], "Making migrations"):
        print_error("Failed to make migrations")
        return
    
    # Step 2: Run migrations
    if not run_command([sys.executable, 'manage.py', 'migrate'], "Running migrations"):
        print_error("Failed to run migrations")
        return
    
    # Step 3: Start server
    print_step("Starting Django server")
    print_success("Server starting...")
    print("\n📍 Available URLs:")
    print("   Main Application: http://localhost:8000/")
    print("   Admin Panel: http://localhost:8000/admin/")
    
    print("\n📝 To enable API features:")
    print("   1. Install: pip install djangorestframework drf-yasg")
    print("   2. Install: pip install google-generativeai python-dotenv")
    print("   3. Uncomment API settings in settings.py")
    print("   4. Restart server")
    
    print("\n" + "=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        subprocess.run([sys.executable, 'manage.py', 'runserver'])
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")

if __name__ == "__main__":
    main()
