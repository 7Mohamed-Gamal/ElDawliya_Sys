# Quick Start: Database Configuration

## 🚀 5-Minute Setup Guide

### Prerequisites
- ✅ SQL Server installed (Express or Full version)
- ✅ Python 3.8+ installed
- ✅ Virtual environment activated

### Step 1: Install ODBC Driver

Download and install: [ODBC Driver 17 for SQL Server](https://go.microsoft.com/fwlink/?linkid=2249004)

### Step 2: Configure Database

Open SQL Server Management Studio (SSMS) and run:

```sql
-- Create database
CREATE DATABASE ElDawliya_Sys
COLLATE Arabic_CI_AS;
GO

-- Create login (if needed)
CREATE LOGIN eldawliya_user WITH PASSWORD = 'YourStrong@Passw0rd';
GO

-- Grant permissions
USE ElDawliya_Sys;
CREATE USER eldawliya_user FOR LOGIN eldawliya_user;
ALTER ROLE db_owner ADD MEMBER eldawliya_user;
GO
```

### Step 3: Update .env File

Edit `ElDawliya_Sys/.env`:

```bash
# Database Configuration
DB_ENGINE=mssql
DB_NAME=ElDawliya_Sys
DB_HOST=localhost
DB_PORT=1433
DB_USER=eldawliya_user
DB_PASSWORD=YourStrong@Passw0rd
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUSTED=no
```

### Step 4: Install Dependencies

```bash
cd ElDawliya_Sys
pip install -r requirements.txt
```

### Step 5: Run Migrations

```bash
# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 6: Start Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000/admin

---

## ✅ Verification

Test your configuration:

```bash
# Check for issues
python manage.py check

# Test database connection
python manage.py dbshell
```

---

## 🔄 Switch to SQLite (Development Only)

For quick testing without SQL Server:

Edit `.env`:

```bash
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
```

Then run:

```bash
python manage.py migrate
python manage.py runserver
```

---

## 🐛 Troubleshooting

### "ODBC Driver not found"
- Install ODBC Driver 17 or 18
- Verify exact name in `.env` matches installed driver

### "Login failed"
- Check `DB_USER` and `DB_PASSWORD` in `.env`
- Verify user exists in SQL Server
- Ensure SQL Server Authentication is enabled

### "Database does not exist"
- Create database using SSMS (Step 2)
- Verify `DB_NAME` matches exactly

---

## 📚 Next Steps

- [Full Database Configuration Guide](DATABASE_CONFIGURATION.md)
- [Django Documentation](https://docs.djangoproject.com/)
- [SQL Server Documentation](https://docs.microsoft.com/sql/)
