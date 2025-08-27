#!/usr/bin/env python3
"""
HR URLs Validation Script
========================

This script validates all HR-related URL patterns to ensure they resolve correctly.
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_Sys.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from django.test import RequestFactory

def test_hr_urls():
    """Test all HR-related URL patterns."""
    
    hr_urls = [
        # Employees
        'employees:dashboard',
        'employees:employee_list',
        
        # Attendance  
        'attendance:dashboard',
        'attendance:mark_attendance',
        'attendance:leave_balance_list',
        
        # Payrolls
        'payrolls:dashboard',
        
        # Leaves
        'leaves:dashboard',
        
        # Insurance
        'insurance:dashboard',
        
        # Evaluations
        'evaluations:dashboard',
        
        # Training (under construction)
        'training:dashboard',
        
        # Loans (under construction)
        'loans:dashboard',
        
        # Reports
        'reports:dashboard',
        
        # Cars (already verified)
        'cars:dashboard',
        'cars:car_list',
        'cars:supplier_list',
        'cars:trip_list',
    ]
    
    print("🔍 Testing HR URL patterns...")
    print("=" * 50)
    
    success_count = 0
    error_count = 0
    
    for url_name in hr_urls:
        try:
            url = reverse(url_name)
            print(f"✅ {url_name:<30} -> {url}")
            success_count += 1
        except NoReverseMatch as e:
            print(f"❌ {url_name:<30} -> ERROR: {e}")
            error_count += 1
        except Exception as e:
            print(f"⚠️  {url_name:<30} -> UNEXPECTED ERROR: {e}")
            error_count += 1
    
    print("=" * 50)
    print(f"📊 Results: {success_count} successful, {error_count} errors")
    
    if error_count == 0:
        print("🎉 All HR URL patterns are working correctly!")
        return True
    else:
        print("⚠️  Some URL patterns have issues that need to be fixed.")
        return False

if __name__ == '__main__':
    success = test_hr_urls()
    sys.exit(0 if success else 1)