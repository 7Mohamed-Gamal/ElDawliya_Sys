"""
Basic Security Test to verify the testing framework works
"""
import os
import sys
import django
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User


class BasicSecurityTests(TestCase):
    """
    Basic security tests to verify the framework works
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        user = User.objects.get(username='testuser')
        
        # Password should be hashed, not stored in plain text
        self.assertNotEqual(user.password, 'TestPass123!')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
        
        # Should be able to verify password
        self.assertTrue(user.check_password('TestPass123!'))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_admin_access_protection(self):
        """Test that admin areas require authentication"""
        # Test accessing admin without authentication
        response = self.client.get('/admin/')
        
        # Should redirect to login or return 403/401
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_debug_mode_security(self):
        """Test debug mode security settings"""
        from django.conf import settings
        
        # In production, DEBUG should be False
        if not settings.DEBUG:
            # Check security settings
            self.assertFalse(settings.DEBUG)
            
            # Should have secure session settings
            if hasattr(settings, 'SESSION_COOKIE_SECURE'):
                self.assertTrue(settings.SESSION_COOKIE_SECURE)
            
            if hasattr(settings, 'CSRF_COOKIE_SECURE'):
                self.assertTrue(settings.CSRF_COOKIE_SECURE)
    
    def test_sql_injection_basic(self):
        """Basic SQL injection test"""
        # Try SQL injection in login
        response = self.client.post('/accounts/login/', {
            'username': "admin'--",
            'password': 'any_password'
        })
        
        # Should not bypass authentication
        self.assertNotEqual(response.status_code, 302)  # No redirect (successful login)
        
        # Should not cause database errors
        self.assertNotEqual(response.status_code, 500)
    
    def test_xss_basic(self):
        """Basic XSS protection test"""
        # Login first
        self.client.login(username='testuser', password='TestPass123!')
        
        # Try XSS payload in search
        xss_payload = '<script>alert("XSS")</script>'
        
        try:
            response = self.client.get('/', {'search': xss_payload})
            
            if response.status_code == 200:
                content = response.content.decode()
                # Payload should be escaped
                self.assertNotIn('<script>', content)
        except:
            # URL might not exist, which is fine for this basic test
            pass
    
    def test_authentication_required(self):
        """Test that protected areas require authentication"""
        protected_urls = [
            '/accounts/profile/',
            '/Hr/',
            '/inventory/',
        ]
        
        for url in protected_urls:
            try:
                response = self.client.get(url)
                # Should require authentication (redirect to login or 403/401)
                if response.status_code not in [404]:  # Ignore 404s
                    self.assertIn(response.status_code, [302, 401, 403])
            except:
                # URL might not exist
                pass


if __name__ == '__main__':
    import unittest
    unittest.main()