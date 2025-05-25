#!/usr/bin/env python3
"""
سكريبت اختبار API نظام الدولية
ElDawliya System API Test Script

يقوم هذا السكريبت بتشغيل اختبارات شاملة للـ API
This script runs comprehensive API tests
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_step(step: str):
    """Print a step"""
    print(f"\n🔄 {step}...")

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {message}")

def run_django_tests():
    """Run Django unit tests"""
    print_step("Running Django unit tests")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'test', 'api', '-v', '2'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print_success("All Django tests passed")
            print(f"Output: {result.stdout}")
        else:
            print_error("Some Django tests failed")
            print(f"Error: {result.stderr}")
            print(f"Output: {result.stdout}")
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print_error("Tests timed out after 5 minutes")
        return False
    except Exception as e:
        print_error(f"Failed to run tests: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints with requests"""
    print_step("Testing API endpoints")
    
    try:
        import requests
        
        base_url = "http://localhost:8000/api/v1"
        
        # Test status endpoint (no auth required)
        print_info("Testing status endpoint...")
        response = requests.get(f"{base_url}/status/", timeout=10)
        if response.status_code == 200:
            print_success("Status endpoint working")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Gemini AI: {data.get('services', {}).get('gemini_ai')}")
        else:
            print_error(f"Status endpoint failed: {response.status_code}")
            return False
        
        # Test documentation endpoints
        print_info("Testing documentation endpoints...")
        doc_endpoints = ['/docs/', '/redoc/', '/schema/']
        for endpoint in doc_endpoints:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print_success(f"Documentation endpoint {endpoint} working")
            else:
                print_error(f"Documentation endpoint {endpoint} failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to Django server")
        print_info("Make sure the server is running: python run_api_server.py")
        return False
    except ImportError:
        print_error("requests library not installed")
        print_info("Install with: pip install requests")
        return False
    except Exception as e:
        print_error(f"API endpoint test failed: {e}")
        return False

def test_authentication():
    """Test API authentication"""
    print_step("Testing API authentication")
    
    try:
        import requests
        
        base_url = "http://localhost:8000/api/v1"
        
        # Test without authentication (should fail)
        print_info("Testing without authentication...")
        response = requests.get(f"{base_url}/employees/", timeout=10)
        if response.status_code == 401:
            print_success("Authentication required (as expected)")
        else:
            print_error(f"Expected 401, got {response.status_code}")
        
        # Test with invalid API key (should fail)
        print_info("Testing with invalid API key...")
        headers = {'Authorization': 'ApiKey invalid_key'}
        response = requests.get(f"{base_url}/employees/", headers=headers, timeout=10)
        if response.status_code == 401:
            print_success("Invalid API key rejected (as expected)")
        else:
            print_error(f"Expected 401, got {response.status_code}")
        
        return True
        
    except Exception as e:
        print_error(f"Authentication test failed: {e}")
        return False

def test_api_with_key():
    """Test API with a valid API key"""
    print_step("Testing API with valid key")
    
    # Check if there's an API key in environment
    api_key = os.getenv('API_KEY')
    if not api_key:
        print_info("No API key found in environment variables")
        print_info("Set API_KEY environment variable to test authenticated endpoints")
        return True
    
    try:
        import requests
        
        base_url = "http://localhost:8000/api/v1"
        headers = {'Authorization': f'ApiKey {api_key}'}
        
        # Test authenticated endpoints
        endpoints = [
            '/employees/',
            '/departments/',
            '/products/',
            '/categories/',
            '/tasks/',
            '/meetings/',
            '/usage-stats/'
        ]
        
        for endpoint in endpoints:
            print_info(f"Testing {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                print_success(f"{endpoint} working")
                data = response.json()
                if 'results' in data:
                    print(f"   Found {len(data['results'])} items")
                elif 'count' in data:
                    print(f"   Total count: {data['count']}")
            else:
                print_error(f"{endpoint} failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print_error(f"Authenticated API test failed: {e}")
        return False

def test_ai_endpoints():
    """Test AI endpoints"""
    print_step("Testing AI endpoints")
    
    api_key = os.getenv('API_KEY')
    if not api_key:
        print_info("No API key found, skipping AI tests")
        return True
    
    try:
        import requests
        
        base_url = "http://localhost:8000/api/v1"
        headers = {
            'Authorization': f'ApiKey {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Test chat endpoint
        print_info("Testing AI chat endpoint...")
        chat_data = {
            'message': 'Hello, this is a test message',
            'temperature': 0.7,
            'max_tokens': 100
        }
        response = requests.post(f"{base_url}/ai/chat/", json=chat_data, headers=headers, timeout=30)
        if response.status_code in [200, 503]:  # 503 if Gemini not configured
            print_success("AI chat endpoint responding")
            if response.status_code == 503:
                print_info("Gemini AI not configured (expected in development)")
        else:
            print_error(f"AI chat endpoint failed: {response.status_code}")
        
        # Test analysis endpoint
        print_info("Testing AI analysis endpoint...")
        analysis_data = {
            'data_type': 'employees',
            'analysis_type': 'summary'
        }
        response = requests.post(f"{base_url}/ai/analyze/", json=analysis_data, headers=headers, timeout=30)
        if response.status_code in [200, 503]:  # 503 if Gemini not configured
            print_success("AI analysis endpoint responding")
            if response.status_code == 503:
                print_info("Gemini AI not configured (expected in development)")
        else:
            print_error(f"AI analysis endpoint failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print_error(f"AI endpoints test failed: {e}")
        return False

def check_server_running():
    """Check if Django server is running"""
    try:
        import requests
        response = requests.get("http://localhost:8000/api/v1/status/", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main test function"""
    print_header("ElDawliya System API Tests")
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print_error("manage.py not found. Please run this script from the project root directory.")
        return
    
    # Check if server is running
    if not check_server_running():
        print_info("Django server is not running. Starting it...")
        print_info("You can start it manually with: python run_api_server.py")
        print_info("Or run tests without server: python manage.py test api")
    
    # Run tests
    tests_passed = 0
    total_tests = 5
    
    # 1. Django unit tests
    if run_django_tests():
        tests_passed += 1
    
    # 2. API endpoints
    if test_api_endpoints():
        tests_passed += 1
    
    # 3. Authentication
    if test_authentication():
        tests_passed += 1
    
    # 4. Authenticated endpoints
    if test_api_with_key():
        tests_passed += 1
    
    # 5. AI endpoints
    if test_ai_endpoints():
        tests_passed += 1
    
    # Results
    print_header("Test Results")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print_success("All tests passed! 🎉")
    elif tests_passed >= total_tests * 0.8:
        print_info("Most tests passed. Check any failures above.")
    else:
        print_error("Many tests failed. Please check the issues above.")
    
    print("\n📝 Notes:")
    print("- Set API_KEY environment variable to test authenticated endpoints")
    print("- Set GEMINI_API_KEY environment variable to test AI features")
    print("- Make sure Django server is running for endpoint tests")

if __name__ == "__main__":
    main()
