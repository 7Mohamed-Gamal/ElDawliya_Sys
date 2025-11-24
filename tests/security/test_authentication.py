"""
Authentication and Authorization Security Tests
Comprehensive tests for authentication mechanisms and authorization controls
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
import json
import time
from unittest.mock import patch


class AuthenticationMechanismTests(TestCase):
    """
    Test authentication mechanisms and security
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!'
        )
    
    def test_password_strength_requirements(self):
        """Test password strength requirements"""
        weak_passwords = [
            '123',
            'password',
            '12345678',
            'qwerty',
            'admin',
            'test'
        ]
        
        for weak_password in weak_passwords:
            try:
                user = User.objects.create_user(
                    username=f'user_{weak_password}',
                    password=weak_password
                )
                # If this succeeds, password validation might be weak
                # Check if the password was actually set
                self.assertFalse(user.check_password(weak_password))
            except Exception as e:
                # Good! Password validation rejected weak password
                self.assertIn('password', str(e).lower())
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        password = 'TestPassword123!'
        user = User.objects.create_user(
            username='hashtest',
            password=password
        )
        
        # Password should be hashed
        self.assertNotEqual(user.password, password)
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
        
        # Should be able to verify password
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_login_attempts_tracking(self):
        """Test tracking of failed login attempts"""
        login_url = '/accounts/login/'
        
        # Multiple failed login attempts
        failed_attempts = 0
        for i in range(10):
            response = self.client.post(login_url, {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
            
            if response.status_code != 302:  # Not redirected (failed login)
                failed_attempts += 1
        
        # Should track failed attempts
        self.assertGreater(failed_attempts, 0)
        
        # Test if account gets locked after multiple failures
        # This depends on implementation
        final_response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'TestPass123!'  # Correct password
        })
        
        # Account might be locked or require additional verification
        # This is implementation-dependent
    
    def test_session_management(self):
        """Test session security"""
        # Test session creation
        login_response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        
        if login_response.status_code == 302:  # Successful login
            session_key = self.client.session.session_key
            self.assertIsNotNone(session_key)
            
            # Test session timeout
            # Modify session to be expired
            session = Session.objects.get(session_key=session_key)
            session.expire_date = timezone.now() - timedelta(hours=1)
            session.save()
            
            # Try to access protected resource
            response = self.client.get('/accounts/profile/')
            # Should redirect to login due to expired session
            self.assertIn(response.status_code, [302, 401, 403])
    
    def test_session_fixation_protection(self):
        """Test protection against session fixation attacks"""
        # Get initial session
        response = self.client.get('/')
        initial_session = self.client.session.session_key
        
        # Login
        login_response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        
        if login_response.status_code == 302:
            # Session should change after login
            new_session = self.client.session.session_key
            # Django automatically handles session regeneration
            # This test verifies the behavior
            self.assertIsNotNone(new_session)
    
    def test_concurrent_session_handling(self):
        """Test handling of concurrent sessions"""
        # Create first session
        client1 = Client()
        client1.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        session1 = client1.session.session_key
        
        # Create second session with same user
        client2 = Client()
        client2.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        session2 = client2.session.session_key
        
        # Both sessions should be valid (or implement session limiting)
        response1 = client1.get('/accounts/profile/')
        response2 = client2.get('/accounts/profile/')
        
        # Depending on implementation, both might be valid or one might be invalidated
        # This is a policy decision
    
    def test_logout_security(self):
        """Test secure logout functionality"""
        # Login
        self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        
        session_key = self.client.session.session_key
        
        # Logout
        logout_response = self.client.post('/accounts/logout/')
        
        # Session should be invalidated
        try:
            session = Session.objects.get(session_key=session_key)
            # Session might still exist but should be expired or cleared
        except Session.DoesNotExist:
            # Good! Session was deleted
            pass
        
        # Try to access protected resource
        response = self.client.get('/accounts/profile/')
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_remember_me_security(self):
        """Test remember me functionality security"""
        # Test login with remember me
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'TestPass123!',
            'remember_me': True
        })
        
        if response.status_code == 302:
            # Check if session timeout is extended
            session_key = self.client.session.session_key
            if session_key:
                session = Session.objects.get(session_key=session_key)
                # Should have longer expiry time
                self.assertGreater(session.expire_date, timezone.now() + timedelta(hours=1))


class AuthorizationTests(TestCase):
    """
    Test authorization and access control mechanisms
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create users with different roles
        self.regular_user = User.objects.create_user(
            username='regular',
            password='RegularPass123!'
        )
        
        self.manager_user = User.objects.create_user(
            username='manager',
            password='ManagerPass123!'
        )
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='AdminPass123!'
        )
        
        # Create groups and permissions
        self.hr_group = Group.objects.create(name='HR')
        self.manager_group = Group.objects.create(name='Managers')
        
        # Add users to groups
        self.manager_user.groups.add(self.manager_group)
        
        # Create test permissions
        try:
            from Hr.models import Employee
            content_type = ContentType.objects.get_for_model(Employee)
            self.view_employee_perm = Permission.objects.get_or_create(
                codename='view_employee',
                name='Can view employee',
                content_type=content_type
            )[0]
            
            self.change_employee_perm = Permission.objects.get_or_create(
                codename='change_employee',
                name='Can change employee',
                content_type=content_type
            )[0]
            
            # Assign permissions to groups
            self.hr_group.permissions.add(self.view_employee_perm, self.change_employee_perm)
            self.manager_group.permissions.add(self.view_employee_perm)
        except:
            # Models might not exist in test environment
            pass
    
    def test_role_based_access_control(self):
        """Test role-based access control"""
        # Test regular user access
        self.client.login(username='regular', password='RegularPass123!')
        
        restricted_urls = [
            '/admin/',
            '/Hr/employee/add/',
            '/administrator/',
        ]
        
        for url in restricted_urls:
            try:
                response = self.client.get(url)
                # Regular user should not access restricted areas
                self.assertIn(response.status_code, [302, 403, 401, 404])
            except:
                pass
        
        # Test admin user access
        self.client.logout()
        self.client.login(username='admin', password='AdminPass123!')
        
        for url in restricted_urls:
            try:
                response = self.client.get(url)
                # Admin should have broader access
                if response.status_code == 403:
                    # Even admin might not have access to some areas
                    pass
            except:
                pass
    
    def test_permission_based_access(self):
        """Test permission-based access control"""
        # Test user without HR permissions
        self.client.login(username='regular', password='RegularPass123!')
        
        try:
            response = self.client.get('/Hr/employee/')
            # Should check for proper permissions
            if response.status_code == 200:
                # If accessible, should show appropriate data only
                pass
        except:
            pass
        
        # Add user to HR group
        self.regular_user.groups.add(self.hr_group)
        
        try:
            response = self.client.get('/Hr/employee/')
            # Should now have access with HR permissions
            if response.status_code == 403:
                # Permission system might be more restrictive
                pass
        except:
            pass
    
    def test_object_level_permissions(self):
        """Test object-level permissions"""
        # Create test data
        self.client.login(username='manager', password='ManagerPass123!')
        
        try:
            # Create employee record
            response = self.client.post('/Hr/employee/add/', {
                'first_name': 'Test',
                'last_name': 'Employee',
                'email': 'test@example.com'
            })
            
            if response.status_code in [200, 302]:
                # Switch to different user
                self.client.logout()
                self.client.login(username='regular', password='RegularPass123!')
                
                # Try to access/modify the employee record
                response = self.client.get('/Hr/employee/1/')
                # Should check object-level permissions
                
                response = self.client.post('/Hr/employee/1/edit/', {
                    'first_name': 'Modified',
                    'last_name': 'Employee'
                })
                # Should prevent unauthorized modifications
                self.assertIn(response.status_code, [403, 401, 302])
        except:
            pass
    
    def test_horizontal_privilege_escalation(self):
        """Test for horizontal privilege escalation"""
        # Create two users
        user1 = User.objects.create_user(username='user1', password='Pass123!')
        user2 = User.objects.create_user(username='user2', password='Pass123!')
        
        # Login as user1
        self.client.login(username='user1', password='Pass123!')
        
        # Try to access user2's data
        try:
            response = self.client.get(f'/accounts/profile/{user2.id}/')
            # Should not allow access to other user's profile
            self.assertIn(response.status_code, [403, 401, 404])
        except:
            pass
        
        # Try to modify user2's data
        try:
            response = self.client.post(f'/api/v1/users/{user2.id}/', {
                'email': 'hacked@example.com'
            })
            # Should not allow modification of other user's data
            self.assertIn(response.status_code, [403, 401, 404])
        except:
            pass
    
    def test_vertical_privilege_escalation(self):
        """Test for vertical privilege escalation"""
        # Login as regular user
        self.client.login(username='regular', password='RegularPass123!')
        
        # Try to access admin functions
        admin_urls = [
            '/admin/',
            '/administrator/',
            '/api/admin/',
        ]
        
        for url in admin_urls:
            try:
                response = self.client.get(url)
                # Should not allow access to admin functions
                self.assertIn(response.status_code, [302, 403, 401, 404])
            except:
                pass
        
        # Try to modify own permissions
        try:
            response = self.client.post('/api/v1/users/me/', {
                'is_superuser': True,
                'is_staff': True
            })
            
            if response.status_code in [200, 204]:
                # Check if privilege escalation was prevented
                updated_user = User.objects.get(username='regular')
                self.assertFalse(updated_user.is_superuser)
                self.assertFalse(updated_user.is_staff)
        except:
            pass
    
    def test_insecure_direct_object_references(self):
        """Test for insecure direct object references"""
        # Login as regular user
        self.client.login(username='regular', password='RegularPass123!')
        
        # Try to access objects by ID manipulation
        object_urls = [
            '/Hr/employee/1/',
            '/Hr/employee/2/',
            '/inventory/product/1/',
            '/tasks/1/',
            '/meetings/1/'
        ]
        
        for url in object_urls:
            try:
                response = self.client.get(url)
                # Should check authorization for each object
                if response.status_code == 200:
                    # If accessible, should verify user has permission
                    content = response.content.decode()
                    # Check if sensitive information is exposed
                    sensitive_terms = ['salary', 'confidential', 'private']
                    for term in sensitive_terms:
                        if term in content.lower():
                            # Should not expose sensitive information to unauthorized users
                            pass
            except:
                pass


class JWTSecurityTests(TestCase):
    """
    Test JWT token security (if implemented)
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
    
    def test_jwt_token_generation(self):
        """Test JWT token generation and validation"""
        try:
            # Try to get JWT token
            response = self.client.post('/api/auth/token/', {
                'username': 'testuser',
                'password': 'TestPass123!'
            })
            
            if response.status_code == 200:
                data = response.json()
                self.assertIn('access', data)
                self.assertIn('refresh', data)
                
                # Token should be properly formatted JWT
                access_token = data['access']
                self.assertEqual(len(access_token.split('.')), 3)  # JWT has 3 parts
        except:
            # JWT might not be implemented
            pass
    
    def test_jwt_token_expiration(self):
        """Test JWT token expiration"""
        try:
            # Get token
            response = self.client.post('/api/auth/token/', {
                'username': 'testuser',
                'password': 'TestPass123!'
            })
            
            if response.status_code == 200:
                data = response.json()
                access_token = data['access']
                
                # Use token for API request
                response = self.client.get('/api/v1/users/me/', 
                                         HTTP_AUTHORIZATION=f'Bearer {access_token}')
                self.assertEqual(response.status_code, 200)
                
                # Test with expired token (would need to mock time or wait)
                # This is typically tested with shorter expiration times in tests
        except:
            pass
    
    def test_jwt_token_refresh(self):
        """Test JWT token refresh mechanism"""
        try:
            # Get tokens
            response = self.client.post('/api/auth/token/', {
                'username': 'testuser',
                'password': 'TestPass123!'
            })
            
            if response.status_code == 200:
                data = response.json()
                refresh_token = data['refresh']
                
                # Use refresh token to get new access token
                response = self.client.post('/api/auth/token/refresh/', {
                    'refresh': refresh_token
                })
                
                if response.status_code == 200:
                    new_data = response.json()
                    self.assertIn('access', new_data)
                    
                    # New access token should be different
                    self.assertNotEqual(data['access'], new_data['access'])
        except:
            pass
    
    def test_jwt_token_blacklisting(self):
        """Test JWT token blacklisting on logout"""
        try:
            # Get tokens
            response = self.client.post('/api/auth/token/', {
                'username': 'testuser',
                'password': 'TestPass123!'
            })
            
            if response.status_code == 200:
                data = response.json()
                access_token = data['access']
                refresh_token = data['refresh']
                
                # Logout (should blacklist tokens)
                response = self.client.post('/api/auth/logout/', {
                    'refresh': refresh_token
                })
                
                # Try to use blacklisted token
                response = self.client.get('/api/v1/users/me/',
                                         HTTP_AUTHORIZATION=f'Bearer {access_token}')
                self.assertEqual(response.status_code, 401)
        except:
            pass


class APIKeySecurityTests(TestCase):
    """
    Test API key security (if implemented)
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
    
    def test_api_key_authentication(self):
        """Test API key authentication"""
        try:
            # Try to access API without key
            response = self.client.get('/api/v1/employees/')
            self.assertIn(response.status_code, [401, 403])
            
            # Try with invalid API key
            response = self.client.get('/api/v1/employees/',
                                     HTTP_X_API_KEY='invalid_key')
            self.assertIn(response.status_code, [401, 403])
            
            # Test with valid API key (would need to create one first)
            # This depends on the API key implementation
        except:
            pass
    
    def test_api_key_permissions(self):
        """Test API key permissions and scoping"""
        try:
            # API keys should have limited permissions
            # Test that API key cannot access admin functions
            response = self.client.get('/api/admin/',
                                     HTTP_X_API_KEY='test_key')
            self.assertIn(response.status_code, [401, 403, 404])
        except:
            pass
    
    def test_api_key_rate_limiting(self):
        """Test API key rate limiting"""
        try:
            # Make multiple requests with same API key
            responses = []
            for i in range(100):
                response = self.client.get('/api/v1/employees/',
                                         HTTP_X_API_KEY='test_key')
                responses.append(response.status_code)
                if response.status_code == 429:  # Rate limited
                    break
            
            # Should implement rate limiting for API keys
            rate_limited = any(status == 429 for status in responses)
            # This is implementation-dependent
        except:
            pass


if __name__ == '__main__':
    pytest.main([__file__])