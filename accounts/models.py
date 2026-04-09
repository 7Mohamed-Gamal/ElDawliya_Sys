from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Users_Login_New(AbstractUser):
    """
    Custom user model for the ElDawliya System.
    
    This model extends the standard Django AbstractUser to include role-based 
    access control and customized group/permission relationships.
    
    نموذج المستخدم المخصص لنظام الدولية.
    يوسع هذا النموذج AbstractUser القياسي في Django ليشمل التحكم في الوصول القائم على الأدوار
    وعلاقات المجموعات والأذونات المخصصة.
    """
    
    # User role for access control
    Role = models.CharField(
        max_length=20, 
        choices=[('admin', 'Admin'), ('manager', 'Manager'), ('employee', 'Employee')],
        verbose_name='الدور'
    )
    
    groups = models.ManyToManyField(
        Group,
        related_name='users_login_new_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='المجموعات',
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='users_login_new_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='أذونات المستخدم',
    )

    def __str__(self):
        """Returns the username as the string representation of the user."""
        return self.username

    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمين'
