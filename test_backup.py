import pyodbc
import os

print('Attempting to backup...')
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=ELDAWLIYA-SYSTE;DATABASE=ElDawliya_Sys;UID=admin;PWD=hgslduhgfwdv', timeout=5, autocommit=True)
cursor = conn.cursor()

# Create backups directory if it doesn't exist
backup_dir = os.path.join(os.getcwd(), 'backups')
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

# Use a location that SQL Server service can access
backup_path = 'C:\\temp\\ElDawliya_Sys_backup.bak'

backup_sql = f"BACKUP DATABASE [ElDawliya_Sys] TO DISK = N'{backup_path}' WITH COMPRESSION"
print(f'Executing: {backup_sql}')

try:
    # Execute backup without explicit transaction
    cursor.execute(backup_sql)
    # No need for cursor.commit() for backup operations
    print('Backup successful!')
except Exception as e:
    print(f'Backup failed: {str(e)}')

cursor.close()
conn.close()
