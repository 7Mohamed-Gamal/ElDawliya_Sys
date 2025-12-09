from django.db import models
from apps.hr.employees.models import Employee


class AssetCategory(models.Model):
    """AssetCategory class"""
    category_id = models.AutoField(primary_key=True, db_column='CategoryID')
    category_name = models.CharField(max_length=100, db_column='CategoryName')

    class Meta:
        """Meta class"""
        db_table = 'AssetCategories'
        verbose_name = 'تصنيف أصل'
        verbose_name_plural = 'تصنيفات الأصول'


class Asset(models.Model):
    """Asset class"""
    asset_id = models.AutoField(primary_key=True, db_column='AssetID')
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, db_column='CategoryID', blank=True, null=True)
    asset_name = models.CharField(max_length=150, db_column='AssetName')
    serial_no = models.CharField(max_length=100, db_column='SerialNo', blank=True, null=True)
    purchase_date = models.DateField(db_column='PurchaseDate', blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=18, decimal_places=2, db_column='PurchasePrice', blank=True, null=True)
    status = models.CharField(max_length=30, db_column='Status', default='Available')

    class Meta:
        """Meta class"""
        db_table = 'Assets'
        verbose_name = 'أصل'
        verbose_name_plural = 'الأصول'


class EmployeeAsset(models.Model):
    """EmployeeAsset class"""
    emp_asset_id = models.AutoField(primary_key=True, db_column='EmpAssetID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, db_column='AssetID')
    assigned_date = models.DateField(db_column='AssignedDate', blank=True, null=True)
    return_date = models.DateField(db_column='ReturnDate', blank=True, null=True)
    condition_notes = models.CharField(max_length=500, db_column='ConditionNotes', blank=True, null=True)

    class Meta:
        """Meta class"""
        db_table = 'EmployeeAssets'
        verbose_name = 'أصل موظف'
        verbose_name_plural = 'أصول الموظفين'

# Create your models here.
