@echo off
echo ========================================
echo   Testing Dashboard Fixes
echo ========================================
echo.

echo Step 1: Checking system...
python manage.py check

echo.
echo Step 2: Running migrations...
python manage.py migrate

echo.
echo Step 3: Starting server...
echo.
echo ========================================
echo   Fixed Issues:
echo ========================================
echo - Fixed 'create_user' URL namespace error
echo - Fixed 'edit_permissions' URL namespace error
echo - Added edit_permissions view and URL
echo - Updated edit_permissions template
echo - Fixed 'IsActive' field name error
echo.
echo Available URLs:
echo - Home: http://localhost:8000/accounts/home/
echo - Dashboard: http://localhost:8000/accounts/dashboard/
echo - Admin: http://localhost:8000/admin/
echo.
echo Dashboard Features:
echo - View all users
echo - Create new user
echo - Edit user permissions
echo - User statistics
echo.
echo API Features:
echo - API Dashboard: http://localhost:8000/api/v1/dashboard/
echo - AI Chat: http://localhost:8000/api/v1/ai/chat-interface/
echo - Data Analysis: http://localhost:8000/api/v1/ai/analysis-interface/
echo - API Docs: http://localhost:8000/api/v1/docs/
echo.
echo Login: admin / admin123
echo.
echo ========================================

python manage.py runserver
