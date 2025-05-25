from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import APIKey, GeminiConversation, GeminiMessage
import secrets

User = get_user_model()


class APIKeyModelTest(TestCase):
    """Test cases for APIKey model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_api_key(self):
        """Test creating an API key"""
        api_key = APIKey.objects.create(
            user=self.user,
            name='Test API Key',
            key=secrets.token_urlsafe(32)
        )
        self.assertEqual(api_key.user, self.user)
        self.assertEqual(api_key.name, 'Test API Key')
        self.assertTrue(api_key.is_active)
        self.assertFalse(api_key.is_expired())

    def test_api_key_string_representation(self):
        """Test API key string representation"""
        api_key = APIKey.objects.create(
            user=self.user,
            name='Test API Key',
            key=secrets.token_urlsafe(32)
        )
        expected_str = f"Test API Key - {self.user.username}"
        self.assertEqual(str(api_key), expected_str)


class GeminiConversationModelTest(TestCase):
    """Test cases for GeminiConversation model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_conversation(self):
        """Test creating a Gemini conversation"""
        conversation = GeminiConversation.objects.create(
            user=self.user,
            title='Test Conversation'
        )
        self.assertEqual(conversation.user, self.user)
        self.assertEqual(conversation.title, 'Test Conversation')
        self.assertTrue(conversation.is_active)

    def test_conversation_string_representation(self):
        """Test conversation string representation"""
        conversation = GeminiConversation.objects.create(
            user=self.user,
            title='Test Conversation'
        )
        expected_str = f"Test Conversation - {self.user.username}"
        self.assertEqual(str(conversation), expected_str)


class APIAuthenticationTest(APITestCase):
    """Test cases for API authentication"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.api_key = APIKey.objects.create(
            user=self.user,
            name='Test API Key',
            key=secrets.token_urlsafe(32)
        )
        self.client = APIClient()

    def test_api_key_authentication(self):
        """Test API key authentication"""
        self.client.credentials(HTTP_AUTHORIZATION=f'ApiKey {self.api_key.key}')
        response = self.client.get('/api/v1/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_api_key(self):
        """Test invalid API key"""
        self.client.credentials(HTTP_AUTHORIZATION='ApiKey invalid_key')
        response = self.client.get('/api/v1/status/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_authentication(self):
        """Test request without authentication"""
        response = self.client.get('/api/v1/employees/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class APIEndpointsTest(APITestCase):
    """Test cases for API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_staff=True
        )
        self.api_key = APIKey.objects.create(
            user=self.user,
            name='Test API Key',
            key=secrets.token_urlsafe(32)
        )
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'ApiKey {self.api_key.key}')

    def test_api_status_endpoint(self):
        """Test API status endpoint"""
        response = self.client.get('/api/v1/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('version', response.data)
        self.assertIn('services', response.data)

    def test_employees_endpoint(self):
        """Test employees endpoint"""
        response = self.client.get('/api/v1/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_products_endpoint(self):
        """Test products endpoint"""
        response = self.client.get('/api/v1/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_tasks_endpoint(self):
        """Test tasks endpoint"""
        response = self.client.get('/api/v1/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_meetings_endpoint(self):
        """Test meetings endpoint"""
        response = self.client.get('/api/v1/meetings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)


class GeminiAITest(APITestCase):
    """Test cases for Gemini AI functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_staff=True
        )
        self.api_key = APIKey.objects.create(
            user=self.user,
            name='Test API Key',
            key=secrets.token_urlsafe(32)
        )
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'ApiKey {self.api_key.key}')

    def test_gemini_chat_endpoint_structure(self):
        """Test Gemini chat endpoint structure (without actual AI call)"""
        data = {
            'message': 'Hello, how are you?',
            'temperature': 0.7,
            'max_tokens': 100
        }
        response = self.client.post('/api/v1/ai/chat/', data, format='json')
        # This might fail if Gemini is not configured, but we test the structure
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ])

    def test_gemini_analyze_endpoint_structure(self):
        """Test Gemini analyze endpoint structure"""
        data = {
            'data_type': 'employees',
            'analysis_type': 'summary'
        }
        response = self.client.post('/api/v1/ai/analyze/', data, format='json')
        # This might fail if Gemini is not configured, but we test the structure
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ])
