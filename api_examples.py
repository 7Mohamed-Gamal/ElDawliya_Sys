#!/usr/bin/env python3
"""
أمثلة لاستخدام API نظام الدولية
Examples for using ElDawliya System API

تأكد من تعيين متغيرات البيئة التالية:
Make sure to set the following environment variables:
- API_BASE_URL: Base URL for the API (default: http://localhost:8000/api/v1/)
- API_KEY: Your API key
"""

import os
import requests
import json
from typing import Dict, Any, Optional

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8080/api/v1/')
API_KEY = os.getenv('API_KEY', 'your-api-key-here')

class ElDawliyaAPI:
    """Client for ElDawliya System API"""
    
    def __init__(self, base_url: str = API_BASE_URL, api_key: str = API_KEY):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'ApiKey {api_key}',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response text: {e.response.text}")
            raise
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API status and health check"""
        return self._make_request('GET', '/status/')
    
    def get_employees(self, **params) -> Dict[str, Any]:
        """Get list of employees with optional filters"""
        return self._make_request('GET', '/employees/', params=params)
    
    def get_employee(self, employee_id: int) -> Dict[str, Any]:
        """Get specific employee details"""
        return self._make_request('GET', f'/employees/{employee_id}/')
    
    def get_departments(self) -> Dict[str, Any]:
        """Get list of departments"""
        return self._make_request('GET', '/departments/')
    
    def get_products(self, **params) -> Dict[str, Any]:
        """Get list of products with optional filters"""
        return self._make_request('GET', '/products/', params=params)
    
    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get specific product details"""
        return self._make_request('GET', f'/products/{product_id}/')
    
    def get_tasks(self, **params) -> Dict[str, Any]:
        """Get list of tasks with optional filters"""
        return self._make_request('GET', '/tasks/', params=params)
    
    def get_meetings(self, **params) -> Dict[str, Any]:
        """Get list of meetings with optional filters"""
        return self._make_request('GET', '/meetings/', params=params)
    
    def chat_with_gemini(self, message: str, conversation_id: Optional[str] = None, 
                        temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Chat with Gemini AI"""
        data = {
            'message': message,
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        if conversation_id:
            data['conversation_id'] = conversation_id
        
        return self._make_request('POST', '/ai/chat/', json=data)
    
    def analyze_data(self, data_type: str, analysis_type: str, 
                    filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze system data with Gemini AI"""
        data = {
            'data_type': data_type,
            'analysis_type': analysis_type
        }
        if filters:
            data['filters'] = filters
        
        return self._make_request('POST', '/ai/analyze/', json=data)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return self._make_request('GET', '/usage-stats/')


def main():
    """Main function with examples"""
    print("🚀 ElDawliya System API Examples")
    print("=" * 50)
    
    # Initialize API client
    api = ElDawliyaAPI()
    
    try:
        # 1. Check API status
        print("\n1. 📊 Checking API Status...")
        status = api.get_api_status()
        print(f"   Status: {status['status']}")
        print(f"   Version: {status['version']}")
        print(f"   Gemini AI Available: {status['services']['gemini_ai']}")
        
        # 2. Get employees
        print("\n2. 👥 Getting Employees...")
        employees = api.get_employees(page_size=5)
        print(f"   Total employees: {employees.get('count', 0)}")
        if employees.get('results'):
            for emp in employees['results'][:3]:
                print(f"   - {emp.get('emp_name', 'N/A')} ({emp.get('emp_email', 'N/A')})")
        
        # 3. Search employees by department
        print("\n3. 🔍 Searching Employees by Department...")
        it_employees = api.get_employees(department="تقنية", page_size=3)
        print(f"   IT Department employees: {it_employees.get('count', 0)}")
        
        # 4. Get products
        print("\n4. 📦 Getting Products...")
        products = api.get_products(page_size=5)
        print(f"   Total products: {products.get('count', 0)}")
        if products.get('results'):
            for product in products['results'][:3]:
                print(f"   - {product.get('name', 'N/A')} (Qty: {product.get('quantity', 0)})")
        
        # 5. Get low stock products
        print("\n5. ⚠️ Getting Low Stock Products...")
        low_stock = api.get_products(low_stock=True, page_size=5)
        print(f"   Low stock products: {low_stock.get('count', 0)}")
        
        # 6. Get tasks
        print("\n6. ✅ Getting Tasks...")
        tasks = api.get_tasks(page_size=5)
        print(f"   Total tasks: {tasks.get('count', 0)}")
        
        # 7. Chat with Gemini AI
        print("\n7. 🤖 Chatting with Gemini AI...")
        try:
            chat_response = api.chat_with_gemini(
                "مرحبا! ما هي أهم المعلومات التي يمكنك مساعدتي بها في نظام الدولية؟"
            )
            print(f"   Gemini Response: {chat_response['response'][:200]}...")
            print(f"   Tokens used: {chat_response['tokens_used']}")
        except Exception as e:
            print(f"   Gemini AI not available: {e}")
        
        # 8. Analyze employee data
        print("\n8. 📈 Analyzing Employee Data...")
        try:
            analysis = api.analyze_data(
                data_type='employees',
                analysis_type='summary'
            )
            print(f"   Analysis: {analysis['analysis'][:200]}...")
            print(f"   Data Summary: {analysis['data_summary']}")
        except Exception as e:
            print(f"   Analysis not available: {e}")
        
        # 9. Get usage statistics
        print("\n9. 📊 Getting Usage Statistics...")
        try:
            stats = api.get_usage_stats()
            print(f"   Total requests: {stats['total_requests']}")
            print(f"   Average response time: {stats['avg_response_time']:.3f}s")
            print(f"   Error rate: {stats['error_rate']:.2f}%")
        except Exception as e:
            print(f"   Stats not available: {e}")
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. The Django server is running")
        print("2. Your API key is valid")
        print("3. You have the necessary permissions")


if __name__ == "__main__":
    main()
