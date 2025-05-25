@echo off
echo ========================================
echo   ElDawliya System with AI Configuration
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
echo Step 4: Setting up AI providers...
python manage.py setup_ai_providers

echo.
echo Step 5: Creating superuser (if needed)...
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin', 'admin@eldawliya.com', 'admin123') | python manage.py shell

echo.
echo Step 6: Starting server...
echo.
echo ========================================
echo   System Ready with AI Configuration!
echo ========================================
echo.
echo Available URLs:
echo - Main Application: http://localhost:8000/accounts/home/
echo - Admin Panel: http://localhost:8000/admin/
echo.
echo API Interface:
echo - API Dashboard: http://localhost:8000/api/v1/dashboard/
echo - AI Settings: http://localhost:8000/api/v1/ai/settings/
echo - AI Chat: http://localhost:8000/api/v1/ai/chat-interface/
echo - Data Analysis: http://localhost:8000/api/v1/ai/analysis-interface/
echo - Add AI Config: http://localhost:8000/api/v1/ai/add-config/
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
echo AI Configuration Features:
echo - Support for multiple AI providers (Gemini, OpenAI, Claude, etc.)
echo - Secure API key management
echo - Test connections before saving
echo - Default provider selection
echo - Usage statistics and monitoring
echo.
echo Supported AI Providers:
echo - Google Gemini (gemini-1.5-flash, gemini-1.5-pro)
echo - OpenAI GPT (gpt-3.5-turbo, gpt-4, gpt-4-turbo)
echo - Anthropic Claude (claude-3-sonnet, claude-3-opus)
echo - Hugging Face (various open-source models)
echo - Ollama (local models)
echo - Custom providers
echo.
echo Next Steps:
echo 1. Go to AI Settings: http://localhost:8000/api/v1/ai/settings/
echo 2. Add your API keys for desired providers
echo 3. Test connections to ensure they work
echo 4. Set a default provider for AI chat
echo 5. Start using AI features!
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python manage.py runserver
