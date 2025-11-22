@echo off
echo ========================================
echo Running Code Quality Checks
echo ========================================

echo.
echo [1/5] Running Flake8...
python -m flake8 --max-line-length=120 --exclude=migrations,venv,env,.git,__pycache__,.pytest_cache --statistics --count > flake8_report.txt 2>&1

echo.
echo [2/5] Running Bandit Security Check...
python -m bandit -r . -x ./venv,./env,./migrations,./.git -f txt -o bandit_report.txt 2>&1

echo.
echo [3/5] Running Safety Check...
python -m safety check --json > safety_report.json 2>&1

echo.
echo [4/5] Checking Django Configuration...
python manage.py check --deploy > django_check.txt 2>&1

echo.
echo [5/5] Checking for Missing Migrations...
python manage.py makemigrations --dry-run --check > migrations_check.txt 2>&1

echo.
echo ========================================
echo All checks completed!
echo Reports saved to:
echo - flake8_report.txt
echo - bandit_report.txt
echo - safety_report.json
echo - django_check.txt
echo - migrations_check.txt
echo ========================================

