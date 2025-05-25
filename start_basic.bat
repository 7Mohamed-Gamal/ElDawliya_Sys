@echo off
echo ========================================
echo    ElDawliya System - Basic Start
echo ========================================
echo.

echo Step 1: Making migrations...
python manage.py makemigrations

echo.
echo Step 2: Running migrations...
python manage.py migrate

echo.
echo Step 3: Starting server...
echo.
echo Available URLs:
echo - Main App: http://localhost:8000/
echo - Admin: http://localhost:8000/admin/
echo.
echo Note: API features are disabled until dependencies are installed
echo To enable API: pip install djangorestframework drf-yasg google-generativeai
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python manage.py runserver
