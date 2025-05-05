from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# تعريف الموقع المُخصص للإدارة
class ElDawliyaAdminSite(admin.AdminSite):
    site_title = _("نظام الدولية للإدارة")
    site_header = _("إدارة نظام الدولية")
    index_title = _("لوحة التحكم")
    
    def get_app_list(self, request):
        """
        تخصيص قائمة التطبيقات في الإدارة لتجميع نماذج الصلاحيات معًا
        """
        app_list = super().get_app_list(request)
        
        # تجميع أقسام الصلاحيات
        permission_models = []
        permissions_app = {
            'name': _('نظام الصلاحيات'),
            'app_label': 'permissions',
            'app_url': '#',
            'has_module_perms': True,
            'models': []
        }
        
        # المسار عبر جميع التطبيقات لاستخراج نماذج الصلاحيات
        for app in app_list[:]:
            for model in app['models'][:]:
                # جميع نماذج الصلاحيات
                if ('permission' in model['object_name'].lower() or 
                    'role' in model['object_name'].lower() or 
                    model['object_name'] in ['AppModule', 'Group', 'GroupProfile', 'UserGroup']):
                    
                    # نسخ النموذج إلى قسم الصلاحيات الجديد
                    permissions_app['models'].append(model.copy())
        
        # إضافة قسم الصلاحيات إلى بداية القائمة
        if permissions_app['models']:
            app_list.insert(0, permissions_app)
        
        return app_list

# إنشاء مثيل من الموقع المخصص
admin_site = ElDawliyaAdminSite(name='eldawliya_admin')
