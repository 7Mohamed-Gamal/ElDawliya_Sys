@echo off
echo ========================================
echo   ElDawliya System with API
echo ========================================
echo.

echo Step 1: Installing API requirements...
call install_api_requirements.bat

echo.
echo Step 2: Making API migrations...
python manage.py makemigrations api

echo.
echo Step 3: Running all migrations...
python manage.py migrate

echo.
echo Step 4: Setting up API groups and permissions...
python manage.py setup_api_groups

echo.
echo Step 5: Starting server with API...
echo.
echo Available URLs:
echo - Main App: http://localhost:8000/
echo - Admin: http://localhost:8000/admin/
echo - API Docs: http://localhost:8000/api/v1/docs/
echo - API Status: http://localhost:8000/api/v1/status/
echo - API ReDoc: http://localhost:8000/api/v1/redoc/
echo.
echo API Features:
echo - REST API for all system data
echo - Swagger/OpenAPI documentation
echo - JWT and API Key authentication
echo - AI integration with Gemini
echo - Rate limiting and usage monitoring
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python manage.py runserver
