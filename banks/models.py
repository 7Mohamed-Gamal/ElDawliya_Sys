from django.db import models


class Bank(models.Model):
    bank_id = models.AutoField(primary_key=True, db_column='BankID')
    bank_name = models.CharField(max_length=150, db_column='BankName')
    swift_code = models.CharField(max_length=50, db_column='SwiftCode', blank=True, null=True)

    class Meta:
        db_table = 'Banks'
        verbose_name = 'بنك'
        verbose_name_plural = 'البنوك'

    def __str__(self):
        return self.bank_name

# Create your models here.
