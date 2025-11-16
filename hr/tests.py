from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class HRViewsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pass12345', Role='admin')

    def test_hr_dashboard_authenticated(self):
        self.client.force_login(self.user)
        url = reverse('hr:dashboard')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_hr_dashboard_data_json(self):
        self.client.force_login(self.user)
        url = reverse('hr:dashboard_data')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get('Content-Type'), 'application/json')