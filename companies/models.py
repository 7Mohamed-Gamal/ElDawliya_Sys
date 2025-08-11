from django.db import models


class Company(models.Model):
    company_id = models.AutoField(primary_key=True, db_column='CompanyID')
    name = models.CharField(max_length=200, db_column='CompanyName')
    name_en = models.CharField(max_length=200, db_column='CompanyNameEN', blank=True, null=True)
    tax_number = models.CharField(max_length=50, db_column='TaxNumber', blank=True, null=True)
    commercial_register = models.CharField(max_length=50, db_column='CommercialRegister', blank=True, null=True)
    phone = models.CharField(max_length=50, db_column='Phone', blank=True, null=True)
    email = models.EmailField(max_length=100, db_column='Email', blank=True, null=True)
    website = models.CharField(max_length=255, db_column='Website', blank=True, null=True)
    address = models.CharField(max_length=500, db_column='Address', blank=True, null=True)
    city = models.CharField(max_length=100, db_column='City', blank=True, null=True)
    country = models.CharField(max_length=100, db_column='Country', blank=True, null=True)
    postal_code = models.CharField(max_length=20, db_column='PostalCode', blank=True, null=True)
    is_active = models.BooleanField(db_column='IsActive', default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_column='CreatedAt')
    updated_at = models.DateTimeField(blank=True, null=True, db_column='UpdatedAt')

    class Meta:
        db_table = 'Companies'
        verbose_name = 'شركة'
        verbose_name_plural = 'الشركات'

    def __str__(self):
        return self.name

# Create your models here.
