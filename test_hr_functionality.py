#!/usr/bin/env python
"""
HR Application Functionality Test Script
Tests key HR functionality to ensure everything is working correctly
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

def test_hr_urls():
    """Test that all HR URLs are accessible"""
    print("🔍 Testing HR URL patterns...")
    
    from django.urls import reverse, NoReverseMatch
    
    # List of HR URLs to test
    hr_urls = [
        'Hr:dashboard',
        'Hr:employees:list',
        'Hr:employees:create',
        'Hr:departments:department_list',
        'Hr:departments:department_create',
        'Hr:jobs:job_list',
        'Hr:jobs:job_create',
        'Hr:attendance:attendance_record_list',
        'Hr:attendance:attendance_rule_list',
        'Hr:salaries:salary_item_list',
        'Hr:salaries:payroll_period_list',
        'Hr:salaries:payroll_entry_list',
        'Hr:reports:report_list',
    ]
    
    success_count = 0
    total_count = len(hr_urls)
    
    for url_name in hr_urls:
        try:
            url = reverse(url_name)
            print(f"  ✅ {url_name} → {url}")
            success_count += 1
        except NoReverseMatch as e:
            print(f"  ❌ {url_name} → Error: {e}")
        except Exception as e:
            print(f"  ⚠️  {url_name} → Warning: {e}")
    
    print(f"\n📊 URL Test Results: {success_count}/{total_count} URLs working")
    return success_count == total_count

def test_hr_models():
    """Test HR models can be imported and basic operations work"""
    print("\n🔍 Testing HR Models...")
    
    try:
        # Test model imports
        from Hr.models import Employee, Department, Job
        from Hr.models.legacy_employee import LegacyEmployee as EmployeeModel
        from Hr.models.legacy.legacy_models import LegacyDepartment as DepartmentModel
        from Hr.models.legacy.legacy_models import Job as JobModel
        
        print("  ✅ All HR models imported successfully")
        
        # Test basic model operations
        dept_count = DepartmentModel.objects.count()
        job_count = JobModel.objects.count()
        emp_count = EmployeeModel.objects.count()
        
        print(f"  📊 Database counts:")
        print(f"    - Departments: {dept_count}")
        print(f"    - Jobs: {job_count}")
        print(f"    - Employees: {emp_count}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model test failed: {e}")
        return False

def test_hr_forms():
    """Test HR forms can be imported"""
    print("\n🔍 Testing HR Forms...")
    
    try:
        from Hr.forms.employee_forms import EmployeeForm, DepartmentForm, JobForm
        from Hr.forms.attendance_forms import AttendanceRuleForm
        from Hr.forms.salary_forms import SalaryItemForm
        
        print("  ✅ All HR forms imported successfully")
        
        # Test form instantiation
        emp_form = EmployeeForm()
        dept_form = DepartmentForm()
        job_form = JobForm()
        
        print("  ✅ Forms can be instantiated")
        return True
        
    except Exception as e:
        print(f"  ❌ Form test failed: {e}")
        return False

def test_hr_views():
    """Test HR views can be imported"""
    print("\n🔍 Testing HR Views...")
    
    try:
        from Hr.views.employee_views import dashboard, employee_list, employee_create
        from Hr.views.department_views_updated import department_list, department_create
        from Hr.views.job_views import job_list, job_create
        from Hr.views.salary_views import salary_item_list
        
        print("  ✅ All HR views imported successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ View test failed: {e}")
        return False

def test_template_files():
    """Test that key template files exist"""
    print("\n🔍 Testing Template Files...")
    
    template_files = [
        'Hr/templates/Hr/base.html',
        'Hr/templates/Hr/base_hr.html',
        'Hr/templates/Hr/dashboard.html',
        'Hr/templates/Hr/employees/employee_form.html',
        'Hr/templates/Hr/employees/employee_list.html',
        'Hr/templates/Hr/departments/department_list.html',
        'Hr/templates/Hr/departments/department_form.html',
        'Hr/templates/Hr/jobs/job_list.html',
        'Hr/templates/Hr/jobs/create.html',
        'Hr/templates/Hr/under_construction.html',
    ]
    
    success_count = 0
    total_count = len(template_files)
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"  ✅ {template_file}")
            success_count += 1
        else:
            print(f"  ❌ {template_file} - Not found")
    
    print(f"\n📊 Template Test Results: {success_count}/{total_count} templates found")
    return success_count == total_count

def test_static_files():
    """Test that key static files exist"""
    print("\n🔍 Testing Static Files...")
    
    static_files = [
        'Hr/static/Hr/css/hr_clean.css',
        'static/css/style.css',
    ]
    
    success_count = 0
    total_count = len(static_files)
    
    for static_file in static_files:
        if os.path.exists(static_file):
            print(f"  ✅ {static_file}")
            success_count += 1
        else:
            print(f"  ❌ {static_file} - Not found")
    
    print(f"\n📊 Static Files Test Results: {success_count}/{total_count} files found")
    return success_count == total_count

def main():
    """Run all HR functionality tests"""
    print("🚀 Starting HR Application Functionality Tests")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(("URL Patterns", test_hr_urls()))
    test_results.append(("Models", test_hr_models()))
    test_results.append(("Forms", test_hr_forms()))
    test_results.append(("Views", test_hr_views()))
    test_results.append(("Templates", test_template_files()))
    test_results.append(("Static Files", test_static_files()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed_tests += 1
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! HR application is ready for use.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
