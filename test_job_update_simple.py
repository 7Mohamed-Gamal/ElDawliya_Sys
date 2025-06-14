#!/usr/bin/env python
"""
Simple test to verify employee job update functionality
"""

import requests
import json

def test_employee_list_access():
    """Test if we can access the employee list page"""
    try:
        response = requests.get('http://127.0.0.1:8000/Hr/employees/', timeout=10)
        if response.status_code == 200:
            print("✅ Employee list page accessible")
            return True
        else:
            print(f"❌ Employee list page returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing employee list: {e}")
        return False

def test_employee_edit_page():
    """Test if we can access an employee edit page"""
    try:
        # First get the employee list to find an employee ID
        response = requests.get('http://127.0.0.1:8000/Hr/employees/', timeout=10)
        if response.status_code == 200:
            # Look for employee edit links in the HTML
            if '/Hr/employees/edit/' in response.text:
                print("✅ Employee edit links found in list page")
                
                # Try to access a specific employee edit page (assuming employee ID 11 exists)
                edit_response = requests.get('http://127.0.0.1:8000/Hr/employees/edit/11/', timeout=10)
                if edit_response.status_code == 200:
                    print("✅ Employee edit page accessible")
                    
                    # Check if job selection field is present
                    if 'jop_name' in edit_response.text or 'الوظيفة' in edit_response.text:
                        print("✅ Job selection field found in edit form")
                        return True
                    else:
                        print("❌ Job selection field not found in edit form")
                        return False
                else:
                    print(f"❌ Employee edit page returned status: {edit_response.status_code}")
                    return False
            else:
                print("❌ No employee edit links found")
                return False
        else:
            print(f"❌ Could not access employee list: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing employee edit page: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Employee Job Update Functionality")
    print("=" * 50)
    
    # Test 1: Access employee list
    list_test = test_employee_list_access()
    
    # Test 2: Access employee edit page
    edit_test = test_employee_edit_page()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Employee List Access: {'✅ PASS' if list_test else '❌ FAIL'}")
    print(f"   Employee Edit Access: {'✅ PASS' if edit_test else '❌ FAIL'}")
    
    if list_test and edit_test:
        print("\n🎉 Basic functionality tests passed!")
        print("💡 The employee edit form should now properly handle job title updates.")
        print("   Please test manually by:")
        print("   1. Opening http://127.0.0.1:8000/Hr/employees/")
        print("   2. Clicking 'Edit' on any employee")
        print("   3. Changing the job title/position")
        print("   4. Saving the changes")
        print("   5. Verifying the job title was updated correctly")
    else:
        print("\n💥 Some tests failed. Please check the server and try again.")
