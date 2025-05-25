@echo off
echo ========================================
echo   ElDawliya System - Complete Setup
echo ========================================
echo.

echo Step 1: Installing required packages...
pip install djangorestframework==3.15.2
pip install drf-yasg==1.21.7
pip install djangorestframework-simplejwt==5.3.0
pip install django-cors-headers==4.1.0
pip install google-generativeai==0.8.3
pip install python-dotenv==1.0.1

echo.
echo Step 2: Making migrations...
python manage.py makemigrations
python manage.py makemigrations api

echo.
echo Step 3: Running migrations...
python manage.py migrate

echo.
echo Step 4: Creating superuser (if needed)...
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin', 'admin@eldawliya.com', 'admin123') | python manage.py shell

echo.
echo Step 5: Starting server...
echo.
echo ========================================
echo   System Ready!
echo ========================================
echo.
echo Available URLs:
echo - Main Application: http://localhost:8000/
echo - Admin Panel: http://localhost:8000/admin/
echo - API Documentation: http://localhost:8000/api/v1/docs/
echo - API Status: http://localhost:8000/api/v1/status/
echo - API ReDoc: http://localhost:8000/api/v1/redoc/
echo.
echo Default Admin Login:
echo - Username: admin
echo - Password: admin123
echo.
echo API Features Available:
echo - REST API for all system data
echo - Swagger/OpenAPI documentation
echo - JWT and API Key authentication
echo - AI integration with Gemini (configure GEMINI_API_KEY)
echo - Rate limiting and usage monitoring
echo.
echo To create API key: python manage.py create_api_key admin
echo To setup API groups: python manage.py setup_api_groups
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python manage.py runserver
