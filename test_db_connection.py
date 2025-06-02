import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

# Import the OfficialHoliday model after Django setup
from Hr.models import OfficialHoliday

def test_connection():
    try:
        # Try to query the official holidays
        holidays = OfficialHoliday.objects.all()
        print("Database connection successful!")
        print(f"Found {holidays.count()} official holidays")
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

if __name__ == '__main__':
    test_connection()