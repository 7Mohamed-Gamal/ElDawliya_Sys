from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class AttendanceViewsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='att_user', password='pass12345', Role='admin')

    def test_attendance_dashboard_authenticated(self):
        self.client.force_login(self.user)
        url = reverse('attendance:dashboard')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)