#!/usr/bin/env python
"""
Test script to verify HR salary URL patterns are working correctly
"""

import os
import sys
import django
from django.urls import reverse, NoReverseMatch

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

def test_salary_urls():
    """Test all salary-related URL patterns"""
    print("🔍 Testing HR Salary URL patterns...")
    
    # List of salary URLs to test
    salary_urls = [
        ('Hr:salaries:salary_item_list', {}),
        ('Hr:salaries:salary_item_create', {}),
        ('Hr:salaries:salary_item_edit', {'pk': 1}),
        ('Hr:salaries:salary_item_delete', {'pk': 1}),
        ('Hr:salaries:employee_salary_item_list', {'emp_id': 1}),
        ('Hr:salaries:employee_salary_item_create', {'emp_id': 1}),
        ('Hr:salaries:employee_salary_item_bulk_create', {}),
        ('Hr:salaries:employee_salary_item_edit', {'pk': 1}),
        ('Hr:salaries:employee_salary_item_delete', {'pk': 1}),
        ('Hr:salaries:payroll_calculate', {}),
        ('Hr:salaries:payroll_period_create', {}),
        ('Hr:salaries:payroll_period_edit', {'period_id': 1}),
        ('Hr:salaries:payroll_period_delete', {'period_id': 1}),
        ('Hr:salaries:payroll_entry_list', {}),
        ('Hr:salaries:payroll_entry_detail', {'entry_id': 1}),
        ('Hr:salaries:payroll_entry_approve', {'entry_id': 1}),
        ('Hr:salaries:payroll_entry_reject', {'entry_id': 1}),
        ('Hr:salaries:payroll_period_list', {}),
    ]
    
    success_count = 0
    total_count = len(salary_urls)
    
    for url_name, kwargs in salary_urls:
        try:
            url = reverse(url_name, kwargs=kwargs)
            print(f"  ✅ {url_name} → {url}")
            success_count += 1
        except NoReverseMatch as e:
            print(f"  ❌ {url_name} → Error: {e}")
        except Exception as e:
            print(f"  ⚠️  {url_name} → Warning: {e}")
    
    print(f"\n📊 Salary URL Test Results: {success_count}/{total_count} URLs working")
    return success_count == total_count

def test_salary_models():
    """Test salary models can be imported and accessed"""
    print("\n🔍 Testing Salary Models...")
    
    try:
        from Hr.models.salary_models import (
            SalaryItem, EmployeeSalaryItem, PayrollPeriod, 
            PayrollEntry, PayrollItemDetail
        )
        
        print("  ✅ All salary models imported successfully")
        
        # Test basic model operations
        salary_item_count = SalaryItem.objects.count()
        employee_salary_count = EmployeeSalaryItem.objects.count()
        payroll_period_count = PayrollPeriod.objects.count()
        
        print(f"  📊 Database counts:")
        print(f"    - Salary Items: {salary_item_count}")
        print(f"    - Employee Salary Items: {employee_salary_count}")
        print(f"    - Payroll Periods: {payroll_period_count}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Salary model test failed: {e}")
        return False

def test_salary_views():
    """Test salary views can be imported"""
    print("\n🔍 Testing Salary Views...")
    
    try:
        from Hr.views.salary_views import (
            salary_item_list, salary_item_create, salary_item_edit, salary_item_delete,
            employee_salary_item_list, employee_salary_item_create, 
            employee_salary_item_edit, employee_salary_item_delete,
            payroll_calculate, payroll_period_create, payroll_period_edit
        )
        
        print("  ✅ All salary views imported successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Salary view test failed: {e}")
        return False

def main():
    """Run all salary functionality tests"""
    print("🚀 Starting HR Salary Module Tests")
    print("=" * 50)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Salary URL Patterns", test_salary_urls()))
    test_results.append(("Salary Models", test_salary_models()))
    test_results.append(("Salary Views", test_salary_views()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SALARY MODULE TEST SUMMARY")
    print("=" * 50)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed_tests += 1
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All salary module tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
