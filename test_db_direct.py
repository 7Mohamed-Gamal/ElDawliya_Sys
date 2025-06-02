import os
import pyodbc
from django.conf import settings

def get_connection_string():
    db_config = settings.DATABASES['default']
    conn_str = (
        f"DRIVER={{{db_config['OPTIONS']['driver']}}};"
        f"SERVER={db_config['HOST']};"
        f"DATABASE={db_config['NAME']};"
    )
    
    if db_config['OPTIONS'].get('Trusted_Connection') == 'yes':
        conn_str += "Trusted_Connection=yes;"
    else:
        conn_str += f"UID={db_config['USER']};PWD={db_config['PASSWORD']};"
    
    return conn_str

def test_connection():
    try:
        conn_str = get_connection_string()
        print(f"Attempting connection with: {conn_str}")
        
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()
        
        # Try to query official holidays
        cursor.execute("SELECT COUNT(*) FROM Hr_OfficialHoliday")
        count = cursor.fetchone()[0]
        print(f"Connection successful! Found {count} official holidays")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
    import django
    django.setup()
    test_connection()