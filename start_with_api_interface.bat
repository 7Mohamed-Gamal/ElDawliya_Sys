@echo off
echo ========================================
echo   ElDawliya System with API Interface
echo ========================================
echo.

echo Step 1: Installing API requirements...
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
echo   System Ready with API Interface!
echo ========================================
echo.
echo Available URLs:
echo - Main Application: http://localhost:8000/
echo - Admin Panel: http://localhost:8000/admin/
echo.
echo API Interface (New!):
echo - API Dashboard: http://localhost:8000/api/v1/dashboard/
echo - AI Chat: http://localhost:8000/api/v1/ai/chat-interface/
echo - Data Analysis: http://localhost:8000/api/v1/ai/analysis-interface/
echo - Usage Stats: http://localhost:8000/api/v1/usage-stats-page/
echo.
echo API Documentation:
echo - Swagger UI: http://localhost:8000/api/v1/docs/
echo - ReDoc: http://localhost:8000/api/v1/redoc/
echo - API Status: http://localhost:8000/api/v1/status/
echo.
echo Default Login:
echo - Username: admin
echo - Password: admin123
echo.
echo New Features:
echo - Web interface for API management
echo - AI chat interface in the browser
echo - Data analysis with AI
echo - API usage statistics
echo - Integrated in main navigation
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python manage.py runserver
