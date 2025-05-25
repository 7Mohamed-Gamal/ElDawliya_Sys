#!/usr/bin/env python3
"""
سكريبت تثبيت متطلبات نظام الدولية
ElDawliya System Requirements Installer

يقوم هذا السكريبت بتثبيت جميع المتطلبات اللازمة للنظام
This script installs all required dependencies for the system
"""

import subprocess
import sys
import os
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

def check_python_version():
    """Check Python version"""
    print_step("Checking Python version")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print_error(f"Python 3.7+ required, found {version.major}.{version.minor}")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
    return True

def install_package(package: str, description: str = ""):
    """Install a single package"""
    try:
        print_info(f"Installing {package}...")
        if description:
            print(f"   {description}")
        
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', package
        ], capture_output=True, text=True, check=True)
        
        print_success(f"{package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install {package}")
        print(f"Error: {e.stderr}")
        return False

def install_requirements():
    """Install requirements from requirements.txt"""
    print_step("Installing requirements from requirements.txt")
    
    if not Path('requirements.txt').exists():
        print_error("requirements.txt not found")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True)
        
        print_success("All requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error("Failed to install some requirements")
        print("Trying to install packages individually...")
        return install_individual_packages()

def install_individual_packages():
    """Install packages individually"""
    packages = [
        ('Django==4.2.21', 'Django web framework'),
        ('djangorestframework==3.15.2', 'Django REST Framework'),
        ('drf-yasg==1.21.7', 'Swagger/OpenAPI documentation'),
        ('djangorestframework-simplejwt==5.3.0', 'JWT authentication'),
        ('django-cors-headers==4.1.0', 'CORS headers'),
        ('google-generativeai==0.8.3', 'Google Gemini AI'),
        ('python-dotenv==1.0.1', 'Environment variables'),
        ('django-filter==23.2', 'Filtering'),
        ('django-crispy-forms==2.0', 'Form styling'),
        ('crispy-bootstrap5==0.7', 'Bootstrap 5 forms'),
        ('django-widget-tweaks==1.4.12', 'Widget tweaks'),
        ('pyodbc==4.0.39', 'SQL Server connector'),
        ('mssql-django==1.4.1', 'Django SQL Server backend'),
        ('Pillow==10.3.0', 'Image processing'),
        ('openpyxl==3.1.2', 'Excel files'),
        ('reportlab==3.6.13', 'PDF generation'),
    ]
    
    success_count = 0
    for package, description in packages:
        if install_package(package, description):
            success_count += 1
    
    print(f"\nInstalled {success_count}/{len(packages)} packages")
    return success_count == len(packages)

def check_installation():
    """Check if key packages are installed"""
    print_step("Checking installation")
    
    packages_to_check = [
        'django',
        'rest_framework',
        'drf_yasg',
        'corsheaders',
        'rest_framework_simplejwt',
        'google.generativeai',
        'dotenv'
    ]
    
    installed_count = 0
    for package in packages_to_check:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} ✓")
            installed_count += 1
        except ImportError:
            print_error(f"{package} ✗")
    
    print(f"\nInstalled packages: {installed_count}/{len(packages_to_check)}")
    return installed_count == len(packages_to_check)

def create_env_file():
    """Create .env file if it doesn't exist"""
    print_step("Creating .env file")
    
    if Path('.env').exists():
        print_info(".env file already exists")
        return True
    
    if not Path('.env.example').exists():
        print_error(".env.example not found")
        return False
    
    try:
        # Copy .env.example to .env
        with open('.env.example', 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open('.env', 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print_success(".env file created from .env.example")
        print_info("Please update .env file with your actual configuration")
        return True
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")
        return False

def main():
    """Main installation function"""
    print_header("ElDawliya System Requirements Installer")
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print_error("manage.py not found. Please run this script from the project root directory.")
        return
    
    # Check Python version
    if not check_python_version():
        return
    
    # Upgrade pip first
    print_step("Upgrading pip")
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ], check=True, capture_output=True)
        print_success("pip upgraded")
    except:
        print_info("pip upgrade failed, continuing anyway")
    
    # Install requirements
    if install_requirements():
        print_success("Requirements installation completed")
    else:
        print_error("Some requirements failed to install")
    
    # Check installation
    if check_installation():
        print_success("All key packages are installed")
    else:
        print_error("Some packages are missing")
    
    # Create .env file
    create_env_file()
    
    # Final instructions
    print_header("Installation Complete!")
    print("🎉 Requirements installation finished!")
    print("\nNext steps:")
    print("1. Update .env file with your configuration")
    print("2. Run: python setup_api.py")
    print("3. Run: python run_api_server.py")
    print("\nIf you encounter any issues:")
    print("- Make sure you have Python 3.7+")
    print("- Try running: pip install --upgrade pip")
    print("- Install packages individually if needed")

if __name__ == "__main__":
    main()
