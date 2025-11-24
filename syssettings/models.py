from django.db import models


class SysSetting(models.Model):
    """SysSetting class"""
    setting_id = models.AutoField(primary_key=True, db_column='SettingID')
    setting_key = models.CharField(max_length=100, unique=True, db_column='SettingKey')
    setting_value = models.CharField(max_length=500, db_column='SettingValue', blank=True, null=True)
    description = models.CharField(max_length=255, db_column='Description', blank=True, null=True)

    class Meta:
        """Meta class"""
        db_table = 'SysSettings'
        verbose_name = 'إعداد'
        verbose_name_plural = 'الإعدادات'

    def __str__(self):
        """__str__ function"""
        return self.setting_key

# Create your models here.
