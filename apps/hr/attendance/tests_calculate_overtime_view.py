from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class CalculateOvertimeViewTests(TestCase):
    """CalculateOvertimeViewTests class"""
    def setUp(self):
        """setUp function"""
        User = get_user_model()
        self.user = User.objects.create_user(username='ot_user', password='pass12345', Role='admin')
        self.client.force_login(self.user)

    def test_calculate_overtime_view(self):
        """test_calculate_overtime_view function"""
        url = reverse('attendance:calculate_overtime')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)