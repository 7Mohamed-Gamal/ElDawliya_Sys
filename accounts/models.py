from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Users_Login_New(AbstractUser):
    # نستخدم حقل is_active الموجود في AbstractUser بدلاً من IsActive
    # نحتفظ بحقل Role للتوافق مع الكود الحالي
    Role = models.CharField(max_length=20, choices=[('admin', 'Admin'),('manager', 'Manager'), ('employee', 'Employee')])
    groups = models.ManyToManyField(
        Group,
        related_name='users_login_new_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='users_login_new_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username
        
    # استخدام حقل is_active الموجود في AbstractUser
    @property
    def IsActive(self):
        return self.is_active
        
    @IsActive.setter
    def IsActive(self, value):
        self.is_active = value