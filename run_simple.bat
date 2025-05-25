@echo off
echo ========================================
echo    ElDawliya System - Simple Start
echo ========================================
echo.

echo Installing missing packages...
pip install python-dotenv google-generativeai drf-yasg djangorestframework-simplejwt django-cors-headers

echo.
echo Running migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo Starting server...
echo.
echo Available URLs:
echo - Main App: http://localhost:8000/
echo - Admin: http://localhost:8000/admin/
echo - API Docs: http://localhost:8000/api/v1/docs/
echo - API Status: http://localhost:8000/api/v1/status/
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python manage.py runserver
