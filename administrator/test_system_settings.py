"""
ملف اختبار لإعدادات النظام
يمكن تشغيله للتأكد من أن كل شيء يعمل بشكل صحيح
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from .models import SystemSettings
from .forms import SystemSettingsForm

User = get_user_model()


class SystemSettingsTestCase(TestCase):
    def setUp(self):
        """إعداد البيانات للاختبار"""
        # إنشاء مستخدم مدير
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        # إنشاء عميل للاختبار
        self.client = Client()
        
    def test_system_settings_model_creation(self):
        """اختبار إنشاء نموذج إعدادات النظام"""
        settings = SystemSettings.objects.create(
            company_name="شركة الاختبار",
            system_name="نظام الاختبار",
            timezone="Asia/Riyadh",
            date_format="Y-m-d"
        )
        
        self.assertEqual(settings.company_name, "شركة الاختبار")
        self.assertEqual(settings.system_name, "نظام الاختبار")
        self.assertEqual(settings.timezone, "Asia/Riyadh")
        self.assertEqual(settings.date_format, "Y-m-d")
        
    def test_system_settings_form_validation(self):
        """اختبار التحقق من صحة النموذج"""
        # بيانات صحيحة
        valid_data = {
            'company_name': 'شركة الاختبار',
            'system_name': 'نظام الاختبار',
            'timezone': 'Asia/Riyadh',
            'date_format': 'Y-m-d',
            'language': 'ar',
            'font_family': 'cairo',
            'text_direction': 'rtl',
        }
        
        form = SystemSettingsForm(data=valid_data)
        self.assertTrue(form.is_valid())
        
        # بيانات غير صحيحة (حقول مطلوبة فارغة)
        invalid_data = {
            'company_name': '',
            'system_name': '',
            'timezone': '',
            'date_format': '',
        }
        
        form = SystemSettingsForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        
    def test_system_settings_view_get(self):
        """اختبار عرض صفحة الإعدادات"""
        self.client.login(username='admin', password='testpass123')
        
        url = reverse('administrator:settings')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'إعدادات النظام')
        
    def test_system_settings_view_post_valid(self):
        """اختبار حفظ الإعدادات بنجاح"""
        self.client.login(username='admin', password='testpass123')
        
        data = {
            'company_name': 'شركة الاختبار المحدثة',
            'system_name': 'نظام الاختبار المحدث',
            'timezone': 'Asia/Dubai',
            'date_format': 'd/m/Y',
            'language': 'ar',
            'font_family': 'tajawal',
            'text_direction': 'rtl',
            'enable_debugging': False,
            'maintenance_mode': False,
        }
        
        url = reverse('administrator:settings')
        response = self.client.post(url, data)
        
        # يجب أن يتم إعادة التوجيه بعد الحفظ الناجح
        self.assertEqual(response.status_code, 302)
        
        # التحقق من حفظ البيانات
        settings = SystemSettings.objects.first()
        self.assertEqual(settings.company_name, 'شركة الاختبار المحدثة')
        self.assertEqual(settings.timezone, 'Asia/Dubai')
        
    def test_system_settings_view_post_invalid(self):
        """اختبار حفظ الإعدادات مع بيانات غير صحيحة"""
        self.client.login(username='admin', password='testpass123')
        
        # بيانات غير صحيحة (حقول مطلوبة فارغة)
        data = {
            'company_name': '',
            'system_name': '',
            'timezone': '',
            'date_format': '',
        }
        
        url = reverse('administrator:settings')
        response = self.client.post(url, data)
        
        # يجب أن تبقى في نفس الصفحة مع رسائل خطأ
        self.assertEqual(response.status_code, 200)
        
        # التحقق من وجود رسائل خطأ
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('خطأ' in str(message) for message in messages))


if __name__ == '__main__':
    import django
    import os
    import sys
    
    # إعداد Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ElDawliya_sys.settings')
    django.setup()
    
    # تشغيل الاختبارات
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["administrator.test_system_settings"])
    
    if failures:
        sys.exit(1)
    else:
        print("جميع الاختبارات نجحت!")
