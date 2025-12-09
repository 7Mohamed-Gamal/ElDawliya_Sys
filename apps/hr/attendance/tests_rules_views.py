from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.hr.attendance.models import AttendanceRules


class RulesViewsIntegrationTests(TestCase):
    """RulesViewsIntegrationTests class"""
    def setUp(self):
        """setUp function"""
        User = get_user_model()
        self.user = User.objects.create_user(username='rules_user', password='pass12345', Role='admin')
        self.client.force_login(self.user)

    def test_rules_list_and_create_edit_delete(self):
        """test_rules_list_and_create_edit_delete function"""
        # List
        resp = self.client.get(reverse('attendance:attendance_rules_list'))
        self.assertEqual(resp.status_code, 200)

        # Create
        create_url = reverse('attendance:attendance_rules_create')
        data = {
            'rule_name': 'قاعدة تكامل',
            'late_threshold': 10,
            'early_threshold': 5,
            'week_end_days': 'الجمعة,السبت',
            'is_default': False,
        }
        resp = self.client.post(create_url, data)
        self.assertEqual(resp.status_code, 302)
        rule = AttendanceRules.objects.get(rule_name='قاعدة تكامل')

        # Edit
        edit_url = reverse('attendance:attendance_rules_edit', args=[rule.pk])
        resp = self.client.post(edit_url, {**data, 'late_threshold': 20})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(AttendanceRules.objects.get(pk=rule.pk).late_threshold, 20)

        # Delete
        delete_url = reverse('attendance:attendance_rules_delete', args=[rule.pk])
        resp = self.client.post(delete_url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(AttendanceRules.objects.filter(pk=rule.pk).exists())