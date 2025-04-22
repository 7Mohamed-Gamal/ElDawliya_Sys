from django.db import models
from django.contrib.auth.models import AbstractUser

class Users_Login_New(AbstractUser):
    IsActive = models.BooleanField(default=True)
    Role = models.CharField(max_length=20, choices=[('admin', 'Admin'),('manager', 'Manager'), ('employee', 'Employee')])

    def __str__(self):
        return self.username