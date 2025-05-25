@echo off
echo Testing ElDawliya System...
echo.

echo Step 1: Checking system...
python manage.py check

echo.
echo Step 2: Running migrations...
python manage.py migrate

echo.
echo Step 3: Starting server...
echo.
echo System URLs:
echo - Main: http://localhost:8000/accounts/home/
echo - Admin: http://localhost:8000/admin/
echo - API Dashboard: http://localhost:8000/api/v1/dashboard/
echo.
echo Login: admin / admin123
echo.

python manage.py runserver
