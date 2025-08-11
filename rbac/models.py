from django.db import models


class Role(models.Model):
    role_id = models.AutoField(primary_key=True, db_column='RoleID')
    role_name = models.CharField(max_length=100, db_column='RoleName')
    description = models.CharField(max_length=255, db_column='Description', blank=True, null=True)

    class Meta:
        db_table = 'Roles'
        verbose_name = 'دور'
        verbose_name_plural = 'الأدوار'

    def __str__(self):
        return self.role_name


class Permission(models.Model):
    permission_id = models.AutoField(primary_key=True, db_column='PermissionID')
    permission_key = models.CharField(max_length=100, db_column='PermissionKey', unique=True)
    description = models.CharField(max_length=255, db_column='Description', blank=True, null=True)

    class Meta:
        db_table = 'Permissions'
        verbose_name = 'صلاحية'
        verbose_name_plural = 'الصلاحيات'


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='RoleID')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, db_column='PermissionID')

    class Meta:
        db_table = 'RolePermissions'
        unique_together = [('role', 'permission')]
        verbose_name = 'صلاحية الدور'
        verbose_name_plural = 'صلاحيات الأدوار'


class UserRole(models.Model):
    user_id = models.IntegerField(db_column='UserID')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='RoleID')

    class Meta:
        db_table = 'UserRoles'
        unique_together = [('user_id', 'role')]
        verbose_name = 'دور المستخدم'
        verbose_name_plural = 'أدوار المستخدمين'
