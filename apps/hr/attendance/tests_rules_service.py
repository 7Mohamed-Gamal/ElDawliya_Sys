from django.test import TestCase
from django.conf import settings
from apps.hr.attendance import rules_service
from apps.hr.attendance.models import AttendanceRules


class RulesServiceTests(TestCase):
    """RulesServiceTests class"""
    def test_create_update_delete_legacy_rule(self):
        """test_create_update_delete_legacy_rule function"""
        # Force legacy mode
        setattr(settings, 'ATTENDANCE_USE_MODERN_RULES', False)

        # Create
        obj = rules_service.create_rule({
            'rule_name': 'قاعدة اختبار',
            'late_threshold': 10,
            'early_threshold': 5,
            'week_end_days': 'الجمعة,السبت',
            'is_default': False,
        })
        self.assertIsInstance(obj, AttendanceRules)
        self.assertEqual(obj.rule_name, 'قاعدة اختبار')

        # Update
        updated = rules_service.update_rule(obj.pk, {'late_threshold': 15, 'is_default': True})
        self.assertEqual(updated.late_threshold, 15)
        self.assertTrue(updated.is_default)

        # Set default (idempotent)
        rules_service.set_default_rule(updated.pk)
        self.assertTrue(AttendanceRules.objects.get(pk=updated.pk).is_default)

        # Delete
        rules_service.delete_rule(updated.pk)
        self.assertFalse(AttendanceRules.objects.filter(pk=updated.pk).exists())