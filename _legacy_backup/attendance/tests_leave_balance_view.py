from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class LeaveBalanceViewTests(TestCase):
    """LeaveBalanceViewTests class"""
    def setUp(self):
        """setUp function"""
        User = get_user_model()
        self.user = User.objects.create_user(username='lb_user', password='pass12345', Role='admin')
        self.client.force_login(self.user)

    def test_leave_balance_list_view(self):
        """test_leave_balance_list_view function"""
        url = reverse('attendance:leave_balance_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)