from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class HRViewsTests(TestCase):
    """HRViewsTests class"""
    def setUp(self):
        """setUp function"""
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pass12345', is_superuser=True)

    def test_hr_dashboard_authenticated(self):
        """test_hr_dashboard_authenticated function"""
        self.client.force_login(self.user)
        url = reverse('hr:dashboard')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_hr_dashboard_data_json(self):
        """test_hr_dashboard_data_json function"""
        self.client.force_login(self.user)
        url = reverse('hr:dashboard_data')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get('Content-Type'), 'application/json')

    def test_hr_pages_exist(self):
        """test_hr_pages_exist function"""
        self.client.force_login(self.user)
        for name in ['hr:profile','hr:my_payslips','hr:my_leaves','hr:notifications']:
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 200)