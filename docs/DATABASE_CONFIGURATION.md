# Database Configuration Guide

## Overview

The ElDawliya ERP System uses SQL Server as its primary database, with support for SQLite for development/testing. The database configuration is centralized using environment variables via a `.env` file.

## Configuration Files

### 1. `.env` File (Root Directory)

The main configuration file containing all environment-specific settings.

**Location:** `ElDawliya_Sys/.env`

**Key Variables:**

```bash
# Database Engine Selection
DB_ENGINE=mssql                          # Use 'mssql' for SQL Server, 'django.db.backends.sqlite3' for SQLite

# SQL Server Configuration
DB_NAME=ElDawliya_Sys                    # Database name
DB_HOST=localhost                        # Server address
DB_PORT=1433                             # SQL Server port (default: 1433)
DB_USER=sa                               # Database username
DB_PASSWORD=YourStrong@Passw0rd          # Database password
DB_DRIVER=ODBC Driver 17 for SQL Server  # ODBC driver
DB_TRUSTED=no                            # Use SQL authentication (yes for Windows auth)

# Backup Database (Optional)
BACKUP_DB_NAME=ElDawliya_Sys_Backup
BACKUP_DB_HOST=localhost
BACKUP_DB_PORT=1433
BACKUP_DB_USER=sa
BACKUP_DB_PASSWORD=YourStrong@Passw0rd
```

### 2. `database_config.py`

**Location:** `ElDawliya_sys/database_config.py`

**Purpose:** Reads environment variables and constructs Django DATABASES configuration.

**Features:**
- ✅ Reads all settings from `.env` file
- ✅ Supports both SQL Server and SQLite
- ✅ Configures connection pooling and timeouts
- ✅ Sets Arabic collation (Arabic_CI_AS)
- ✅ Enables MARS (Multiple Active Result Sets)
- ✅ Configures test database names

**Function:**
```python
def get_database_config():
    """Returns database configuration dictionary"""
    return {
        'default': {...},      # Primary database
        'backup': {...},       # Backup database (optional)
    }
```

### 3. `settings/base.py`

**Location:** `ElDawliya_sys/settings/base.py`

**Usage:**
```python
from ElDawliya_sys.database_config import get_database_config

DATABASES = get_database_config()
```

### 4. `settings/config.py` (Legacy - Partially Used)

**Location:** `ElDawliya_sys/settings/config.py`

**Still Used For:**
- Cache configuration
- Email configuration
- Security settings
- API configuration
- Celery configuration
- Logging configuration
- HR system settings

**Note:** Database configuration has been moved to `database_config.py` for better separation of concerns.

## Setup Instructions

### Step 1: Install SQL Server ODBC Driver

Download and install the latest ODBC Driver for SQL Server:
- [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- [ODBC Driver 18 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) (Recommended)

### Step 2: Configure `.env` File

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your database credentials:
   ```bash
   DB_ENGINE=mssql
   DB_NAME=ElDawliya_Sys
   DB_HOST=localhost
   DB_PORT=1433
   DB_USER=sa
   DB_PASSWORD=YourStrong@Passw0rd
   DB_DRIVER=ODBC Driver 17 for SQL Server
   DB_TRUSTED=no
   ```

### Step 3: Create Database

Using SQL Server Management Studio (SSMS) or T-SQL:

```sql
CREATE DATABASE ElDawliya_Sys
COLLATE Arabic_CI_AS;
GO

-- Create login (if not exists)
CREATE LOGIN sa WITH PASSWORD = 'YourStrong@Passw0rd';
GO

-- Grant permissions
USE ElDawliya_Sys;
CREATE USER sa FOR LOGIN sa;
ALTER ROLE db_owner ADD MEMBER sa;
GO
```

### Step 4: Run Migrations

```bash
# Activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 5: Verify Connection

```bash
# Check configuration
python manage.py check

# Test database connection
python manage.py dbshell
```

## Development vs Production

### Development (SQLite)

For quick development without SQL Server:

```bash
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
```

### Production (SQL Server)

For production deployment:

```bash
DB_ENGINE=mssql
DB_NAME=ElDawliya_Sys
DB_HOST=your-server.database.windows.net
DB_PORT=1433
DB_USER=your_admin_user
DB_PASSWORD=your_secure_password
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_TRUSTED=no
```

## Advanced Configuration

### Connection Pooling

SQL Server connection pooling is configured in `database_config.py`:

```python
'OPTIONS': {
    'timeout': 30,              # Connection timeout (seconds)
    'query_timeout': 60,        # Query execution timeout
    'connection_timeout': 30,   # Connection establishment timeout
    'command_timeout': 60,      # Command execution timeout
    'MARS_Connection': 'yes',   # Enable Multiple Active Result Sets
}
```

### SSL/TLS Encryption

For production, enable encryption:

```python
'OPTIONS': {
    'Encrypt': 'yes',
    'TrustServerCertificate': 'no',
}
```

### Windows Authentication

To use Windows Authentication instead of SQL authentication:

```bash
DB_TRUSTED=yes
DB_USER=
DB_PASSWORD=
```

## Database Router

The project uses a custom database router for multi-database support:

**Location:** `ElDawliya_sys/db_router.py`

**Configuration:**
```python
DATABASE_ROUTERS = ['ElDawliya_sys.db_router.DatabaseRouter']
ACTIVE_DB = 'default'
```

## Backup Database

The backup database configuration is optional and can be used for:
- Database replication
- Disaster recovery
- Read-only operations

To enable, configure in `.env`:

```bash
BACKUP_DB_NAME=ElDawliya_Sys_Backup
BACKUP_DB_HOST=localhost
BACKUP_DB_PORT=1433
BACKUP_DB_USER=sa
BACKUP_DB_PASSWORD=YourStrong@Passw0rd
```

## Troubleshooting

### Common Issues

#### 1. ODBC Driver Not Found

**Error:** `Data source name not found and no default driver specified`

**Solution:**
- Install the correct ODBC driver
- Verify driver name matches exactly: `ODBC Driver 17 for SQL Server`
- Check installed drivers: `odbcad32.exe` → Drivers tab

#### 2. Connection Refused

**Error:** `Connection refused` or `Server not found`

**Solution:**
- Verify SQL Server is running
- Check `DB_HOST` and `DB_PORT`
- Ensure firewall allows port 1433
- Test connection: `telnet localhost 1433`

#### 3. Authentication Failed

**Error:** `Login failed for user 'sa'`

**Solution:**
- Verify `DB_USER` and `DB_PASSWORD`
- Enable SQL Server Authentication mode
- Check user permissions in SSMS

#### 4. Database Does Not Exist

**Error:** `Cannot open database "ElDawliya_Sys"`

**Solution:**
```sql
CREATE DATABASE ElDawliya_Sys;
GO
```

### Debug Mode

Enable Django debug mode to see detailed errors:

```bash
DEBUG=True
```

### Database Shell

Test direct database connection:

```bash
python manage.py dbshell
```

## Security Best Practices

1. **Never commit `.env` to version control**
   - Added to `.gitignore`
   - Use `.env.example` for templates

2. **Use strong passwords**
   - Minimum 12 characters
   - Mix of uppercase, lowercase, numbers, symbols

3. **Enable encryption in production**
   - Use SSL/TLS for connections
   - Configure `Encrypt=yes` in OPTIONS

4. **Restrict database permissions**
   - Use least privilege principle
   - Create dedicated application user

5. **Rotate credentials regularly**
   - Change passwords every 90 days
   - Update `.env` file and restart application

## Performance Optimization

### Indexes

Recommended indexes are defined in `database_config.py`:

```python
DATABASE_INDEXES = {
    'Hr_employee': [
        ['employee_number'],
        ['national_id'],
        ['email'],
        ['department_id', 'is_active'],
    ],
    # ... more indexes
}
```

### Query Optimization

- Use `select_related()` for ForeignKey fields
- Use `prefetch_related()` for ManyToMany fields
- Enable MARS for concurrent queries

### Connection Pooling

SQL Server connection pooling is enabled by default in the ODBC driver.

## Monitoring

### Slow Query Logging

Configure in `database_config.py`:

```python
DATABASE_MONITORING = {
    'slow_query_threshold': 1.0,  # seconds
    'log_queries': True,
    'log_slow_queries': True,
}
```

### Health Checks

Use Django's database connection health check:

```python
from django.db import connection

def check_database():
    try:
        connection.ensure_connection()
        return True
    except Exception:
        return False
```

## Migration Guide

### From SQLite to SQL Server

1. Update `.env` file with SQL Server credentials
2. Create empty database in SQL Server
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Migrate data using Django dumpdata/loaddata:
   ```bash
   # Export from SQLite
   python manage.py dumpdata --natural-foreign --natural-primary > data.json
   
   # Import to SQL Server
   python manage.py loaddata data.json
   ```

### Backup and Restore

**Backup:**
```bash
python manage.py dumpdata > backup.json
```

**Restore:**
```bash
python manage.py loaddata backup.json
```

## References

- [Django SQL Server Backend](https://github.com/microsoft/mssql-django)
- [ODBC Driver for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/microsoft-odbc-driver-for-sql-server)
- [Django Database Settings](https://docs.djangoproject.com/en/4.2/ref/settings/#databases)
- [SQL Server Collations](https://docs.microsoft.com/en-us/sql/relational-databases/collations/collation-and-unicode-support)

## Support

For issues or questions:
1. Check this documentation
2. Review Django documentation
3. Check SQL Server logs
4. Contact development team
