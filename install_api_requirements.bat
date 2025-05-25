@echo off
echo ========================================
echo   Installing API Requirements
echo ========================================
echo.

echo Installing Django REST Framework...
pip install djangorestframework==3.15.2

echo Installing API Documentation...
pip install drf-yasg==1.21.7

echo Installing JWT Authentication...
pip install djangorestframework-simplejwt==5.3.0

echo Installing CORS Headers...
pip install django-cors-headers==4.1.0

echo Installing AI Libraries...
pip install google-generativeai==0.8.3

echo Installing Environment Variables...
pip install python-dotenv==1.0.1

echo Installing Django Filter...
pip install django-filter==23.2

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run: python manage.py makemigrations api
echo 2. Run: python manage.py migrate
echo 3. Run: python setup_api.py
echo 4. Run: python manage.py runserver
echo.
echo API will be available at:
echo - API Docs: http://localhost:8000/api/v1/docs/
echo - API Status: http://localhost:8000/api/v1/status/
echo ========================================

pause
