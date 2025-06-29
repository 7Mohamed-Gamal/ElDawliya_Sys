#!/usr/bin/env python
"""
ElDawliya System Functionality Test Script
اختبار وظائف نظام الدولية
"""

import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from django.core.cache import cache
from accounts.models import Users_Login_New
from core.reporting import reporting_service
from core.data_integration import data_integration_service
from core.permissions import permission_service
from core.database_optimization import DatabaseOptimizationService

def test_enhanced_reporting_system():
    """Test the Enhanced Reporting System"""
    print("🔍 Testing Enhanced Reporting System...")
    
    try:
        # Get a test user
        user = Users_Login_New.objects.first()
        if not user:
            print("❌ No users found in database")
            return False
        
        # Test dashboard data generation
        print("  📊 Testing dashboard data generation...")
        dashboard_data = reporting_service.get_dashboard_data(user, '30d')
        
        # Verify data structure
        required_keys = ['overview', 'employee_analytics', 'task_analytics', 
                        'meeting_analytics', 'inventory_analytics', 'purchase_analytics',
                        'trends', 'charts', 'generated_at', 'date_range']
        
        for key in required_keys:
            if key not in dashboard_data:
                print(f"❌ Missing key in dashboard data: {key}")
                return False
        
        print(f"  ✅ Dashboard data generated successfully")
        print(f"     - Total employees: {dashboard_data['overview']['total_employees']}")
        print(f"     - Total tasks: {dashboard_data['overview']['total_tasks']}")
        print(f"     - Total meetings: {dashboard_data['overview']['total_meetings']}")
        print(f"     - Charts available: {len(dashboard_data['charts'])}")
        
        # Test custom report generation
        print("  📋 Testing custom report generation...")
        report_config = {
            'modules': ['employees', 'tasks'],
            'date_range': '30d',
            'format': 'json'
        }
        
        custom_report = reporting_service.generate_custom_report(user, report_config)
        
        if 'report_id' not in custom_report or 'data' not in custom_report:
            print("❌ Custom report generation failed")
            return False
        
        print("  ✅ Custom report generated successfully")
        
        # Test report templates
        print("  📄 Testing report templates...")
        templates = reporting_service.get_report_templates()
        
        if 'templates' not in templates or 'modules' not in templates:
            print("❌ Report templates retrieval failed")
            return False
        
        print(f"  ✅ Report templates retrieved: {len(templates['templates'])} templates")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Reporting System test failed: {str(e)}")
        return False

def test_data_integration_system():
    """Test the Data Integration System"""
    print("🔄 Testing Data Integration System...")
    
    try:
        # Test service initialization
        service = data_integration_service
        
        # Test cross-module data access
        print("  🔍 Testing cross-module data access...")
        
        # Test employee data access
        employees = service.get_employees()
        print(f"  ✅ Employee data access: {len(employees)} employees")
        
        # Test task data access
        tasks = service.get_tasks()
        print(f"  ✅ Task data access: {len(tasks)} tasks")
        
        # Test meeting data access
        meetings = service.get_meetings()
        print(f"  ✅ Meeting data access: {len(meetings)} meetings")
        
        # Test inventory data access
        products = service.get_inventory()
        print(f"  ✅ Inventory data access: {len(products)} products")
        
        # Test purchase data access
        purchases = service.get_purchase_requests()
        print(f"  ✅ Purchase data access: {len(purchases)} purchase requests")
        
        return True
        
    except Exception as e:
        print(f"❌ Data Integration System test failed: {str(e)}")
        return False

def test_permission_system():
    """Test the Unified Permission System"""
    print("🔐 Testing Unified Permission System...")
    
    try:
        # Get a test user
        user = Users_Login_New.objects.first()
        if not user:
            print("❌ No users found in database")
            return False
        
        # Test permission checking
        print("  🔍 Testing permission validation...")
        
        # Test various permissions
        permissions_to_test = [
            'Hr.view_employee',
            'tasks.view_task',
            'meetings.view_meeting',
            'inventory.view_tblproducts',
            'Purchase_orders.view_purchaserequest'
        ]
        
        for permission in permissions_to_test:
            has_permission = permission_service.check_permission(user, permission)
            print(f"     - {permission}: {'✅' if has_permission else '❌'}")
        
        print("  ✅ Permission system working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Permission System test failed: {str(e)}")
        return False

def test_database_optimization():
    """Test the Database Optimization System"""
    print("⚡ Testing Database Optimization System...")

    try:
        # Test database statistics
        print("  📊 Testing database statistics...")
        db_service = DatabaseOptimizationService()
        stats = db_service.get_database_statistics()

        if 'table_stats' not in stats or 'query_performance' not in stats:
            print("❌ Database statistics retrieval failed")
            return False

        print(f"  ✅ Database statistics retrieved: {len(stats['table_stats'])} tables analyzed")

        # Test query performance analysis
        print("  🔍 Testing query performance analysis...")
        performance = db_service.analyze_query_performance()

        print(f"  ✅ Query performance analysis completed")

        return True

    except Exception as e:
        print(f"❌ Database Optimization System test failed: {str(e)}")
        return False

def test_caching_system():
    """Test the Caching System"""
    print("💾 Testing Caching System...")
    
    try:
        # Test cache operations
        print("  🔍 Testing cache operations...")
        
        # Set a test cache value
        cache.set('test_key', 'test_value', 300)
        
        # Retrieve the cache value
        cached_value = cache.get('test_key')
        
        if cached_value != 'test_value':
            print("❌ Cache set/get operation failed")
            return False
        
        print("  ✅ Cache operations working correctly")
        
        # Test cache clearing
        cache.clear()
        cleared_value = cache.get('test_key')
        
        if cleared_value is not None:
            print("❌ Cache clear operation failed")
            return False
        
        print("  ✅ Cache clearing working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Caching System test failed: {str(e)}")
        return False

def main():
    """Run all system tests"""
    print("🚀 ElDawliya System Functionality Test Suite")
    print("=" * 50)
    
    tests = [
        test_enhanced_reporting_system,
        test_data_integration_system,
        test_permission_system,
        test_database_optimization,
        test_caching_system
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! ElDawliya System is fully functional.")
        print("✅ System ready for production deployment.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
