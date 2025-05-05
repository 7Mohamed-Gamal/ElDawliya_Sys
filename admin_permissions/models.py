from django.db import models
from django.contrib.auth.models import Group
from django.conf import settings
from django.utils import timezone

class PermissionAuditLog(models.Model):
    """
    سجل تدقيق لتغييرات الصلاحيات
    """
    ACTION_TYPES = [
        ('add', 'إضافة'),
        ('modify', 'تعديل'),
        ('remove', 'حذف'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                           related_name='admin_permission_audit_logs', verbose_name="المستخدم")
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES, verbose_name="نوع الإجراء")
    department = models.CharField(max_length=100, verbose_name="القسم")
    module = models.CharField(max_length=100, verbose_name="الوحدة")
    permission_type = models.CharField(max_length=20, verbose_name="نوع الصلاحية")
    affected_groups = models.ManyToManyField(Group, blank=True, related_name='admin_audit_logs', verbose_name="المجموعات المتأثرة")
    affected_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                        related_name='admin_affected_audit_logs', verbose_name="المستخدمين المتأثرين")
    description = models.TextField(verbose_name="الوصف")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="التاريخ والوقت")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP")
    additional_data = models.JSONField(null=True, blank=True, verbose_name="بيانات إضافية")

    class Meta:
        verbose_name = "سجل تدقيق الصلاحيات"
        verbose_name_plural = "سجلات تدقيق الصلاحيات"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.department} - {self.module} - {self.timestamp}"

    @classmethod
    def log_permission_change(cls, user, action, department, module, permission_type, description, affected_groups=None, affected_users=None, ip_address=None, data=None):
        """
        تسجيل تغيير في الصلاحيات
        """
        log = cls.objects.create(
            user=user,
            action_type=action,
            department=department,
            module=module,
            permission_type=permission_type,
            description=description,
            ip_address=ip_address,
            additional_data=data
        )

        # إضافة المجموعات المتأثرة
        if affected_groups:
            if isinstance(affected_groups, (list, tuple)):
                log.affected_groups.add(*affected_groups)
            else:
                log.affected_groups.add(affected_groups)

        # إضافة المستخدمين المتأثرين
        if affected_users:
            if isinstance(affected_users, (list, tuple)):
                log.affected_users.add(*affected_users)
            else:
                log.affected_users.add(affected_users)

        return log


class DepartmentPermissionCache(models.Model):
    """
    ذاكرة التخزين المؤقت لصلاحيات الأقسام
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                           related_name='department_permission_cache', verbose_name="المستخدم")
    department_name = models.CharField(max_length=100, verbose_name="اسم القسم")
    has_access = models.BooleanField(default=False, verbose_name="لديه صلاحية الوصول")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        verbose_name = "ذاكرة التخزين المؤقت لصلاحيات الأقسام"
        verbose_name_plural = "ذاكرة التخزين المؤقت لصلاحيات الأقسام"
        unique_together = ['user', 'department_name']

    def __str__(self):
        return f"{self.user.username} - {self.department_name} - {self.has_access}"


class ModulePermissionCache(models.Model):
    """
    ذاكرة التخزين المؤقت لصلاحيات الوحدات
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                           related_name='module_permission_cache', verbose_name="المستخدم")
    department_name = models.CharField(max_length=100, verbose_name="اسم القسم")
    module_name = models.CharField(max_length=100, verbose_name="اسم الوحدة")
    permission_type = models.CharField(max_length=20, verbose_name="نوع الصلاحية")
    has_permission = models.BooleanField(default=False, verbose_name="لديه صلاحية")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        verbose_name = "ذاكرة التخزين المؤقت لصلاحيات الوحدات"
        verbose_name_plural = "ذاكرة التخزين المؤقت لصلاحيات الوحدات"
        unique_together = ['user', 'department_name', 'module_name', 'permission_type']

    def __str__(self):
        return f"{self.user.username} - {self.department_name} - {self.module_name} - {self.permission_type} - {self.has_permission}"
