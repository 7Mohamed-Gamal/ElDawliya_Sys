from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class AppModule(models.Model):
    """
    Represents an application module in the system (e.g., HR, Meetings, Inventory)
    """
    name = models.CharField(max_length=100, verbose_name="اسم التطبيق")
    code = models.CharField(max_length=50, unique=True, verbose_name="كود التطبيق")
    description = models.TextField(blank=True, verbose_name="وصف التطبيق")
    icon = models.CharField(max_length=50, blank=True, verbose_name="أيقونة التطبيق")
    order = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "تطبيق"
        verbose_name_plural = "التطبيقات"
        ordering = ['order', 'name']


class OperationPermission(models.Model):
    """
    Represents a permission for a specific operation (CRUD) in an application module
    """
    PERMISSION_TYPES = [
        ('view', 'عرض'),
        ('add', 'إضافة'),
        ('edit', 'تعديل'),
        ('delete', 'حذف'),
        ('print', 'طباعة'),
    ]

    name = models.CharField(max_length=100, verbose_name="اسم العملية")
    app_module = models.ForeignKey(AppModule, on_delete=models.CASCADE, related_name="operations", verbose_name="التطبيق")
    permission_type = models.CharField(max_length=10, choices=PERMISSION_TYPES, verbose_name="نوع الصلاحية")
    code = models.CharField(max_length=100, verbose_name="كود العملية")
    description = models.TextField(blank=True, verbose_name="وصف العملية")
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    def __str__(self):
        return f"{self.app_module.name} - {self.name} - {self.get_permission_type_display()}"

    class Meta:
        verbose_name = "صلاحية عملية"
        verbose_name_plural = "صلاحيات العمليات"
        unique_together = ['app_module', 'code', 'permission_type']
        ordering = ['app_module__name', 'name', 'permission_type']


class PagePermission(models.Model):
    """
    Represents a permission to access a specific page/template in the system
    """
    name = models.CharField(max_length=100, verbose_name="اسم الصفحة")
    app_module = models.ForeignKey(AppModule, on_delete=models.CASCADE, related_name="pages", verbose_name="التطبيق")
    url_pattern = models.CharField(max_length=255, verbose_name="نمط URL")
    template_path = models.CharField(max_length=255, blank=True, verbose_name="مسار القالب")
    description = models.TextField(blank=True, verbose_name="وصف الصفحة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    def __str__(self):
        return f"{self.app_module.name} - {self.name}"

    class Meta:
        verbose_name = "صلاحية صفحة"
        verbose_name_plural = "صلاحيات الصفحات"
        unique_together = ['app_module', 'url_pattern']
        ordering = ['app_module__name', 'name']


class UserOperationPermission(models.Model):
    """
    Assigns operation permissions to users
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="operation_permissions", verbose_name="المستخدم")
    operation = models.ForeignKey(OperationPermission, on_delete=models.CASCADE, related_name="user_permissions", verbose_name="العملية")
    
    def __str__(self):
        return f"{self.user.username} - {self.operation}"

    class Meta:
        verbose_name = "صلاحية عملية للمستخدم"
        verbose_name_plural = "صلاحيات العمليات للمستخدمين"
        unique_together = ['user', 'operation']


class UserPagePermission(models.Model):
    """
    Assigns page permissions to users
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="page_permissions", verbose_name="المستخدم")
    page = models.ForeignKey(PagePermission, on_delete=models.CASCADE, related_name="user_permissions", verbose_name="الصفحة")
    
    def __str__(self):
        return f"{self.user.username} - {self.page}"

    class Meta:
        verbose_name = "صلاحية صفحة للمستخدم"
        verbose_name_plural = "صلاحيات الصفحات للمستخدمين"
        unique_together = ['user', 'page']