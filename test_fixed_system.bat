@echo off
echo ========================================
echo   Testing Fixed ElDawliya System
echo ========================================
echo.

echo Step 1: Checking system for errors...
python manage.py check

echo.
echo Step 2: Running migrations...
python manage.py migrate

echo.
echo Step 3: Testing URLs...
echo Testing if all URLs are working...

echo.
echo Step 4: Starting server...
echo.
echo ========================================
echo   Fixed Issues:
echo ========================================
echo - Fixed 'employees' namespace error
echo - Fixed 'IsActive' field name error  
echo - Updated all URLs to use correct namespaces
echo.
echo Available URLs:
echo - Home: http://localhost:8000/accounts/home/
echo - Dashboard: http://localhost:8000/accounts/dashboard/
echo - Admin: http://localhost:8000/admin/
echo.
echo New API Features:
echo - API Dashboard: http://localhost:8000/api/v1/dashboard/
echo - AI Chat: http://localhost:8000/api/v1/ai/chat-interface/
echo - Data Analysis: http://localhost:8000/api/v1/ai/analysis-interface/
echo - API Docs: http://localhost:8000/api/v1/docs/
echo.
echo Login: admin / admin123
echo.
echo ========================================

python manage.py runserver
