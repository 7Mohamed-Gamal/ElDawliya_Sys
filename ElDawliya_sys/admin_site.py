from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# تعريف الموقع المُخصص للإدارة
class ElDawliyaAdminSite(admin.AdminSite):
    site_title = _("نظام الدولية للإدارة")
    site_header = _("إدارة نظام الدولية")
    index_title = _("لوحة التحكم")

    def get_app_list(self, request):
        """
        Get the app list for the admin site
        """
        app_list = super().get_app_list(request)
        return app_list

# إنشاء مثيل من الموقع المخصص
admin_site = ElDawliyaAdminSite(name='eldawliya_admin')
