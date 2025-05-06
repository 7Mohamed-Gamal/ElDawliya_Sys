# ملف models.py لتطبيق المخزون
from django.db import models
from django.utils.translation import gettext_lazy as _

class TblCategories(models.Model):
    cat_id = models.IntegerField(db_column='CAT_ID', primary_key=True)
    cat_name = models.CharField(db_column='CAT_Name', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Tbl_Categories'

class TblCustomers(models.Model):
    customer_id = models.IntegerField(db_column='Customer_ID', primary_key=True)
    customer_name = models.CharField(db_column='Customer_Name', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Tbl_Customers'

class TblProducts(models.Model):
    product_id = models.CharField(db_column='Product_ID', primary_key=True, max_length=100, db_collation='Arabic_CI_AS')
    product_name = models.CharField(db_column='Product_Name', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    initial_balance = models.DecimalField(db_column='Initial_Balance', max_digits=18, decimal_places=2, blank=True, null=True)
    elwarad = models.DecimalField(db_column='ElWarad', max_digits=18, decimal_places=2, blank=True, null=True)
    mortagaaomalaa = models.DecimalField(db_column='MortagaaOmalaa', max_digits=18, decimal_places=2, blank=True, null=True)
    elmonsarf = models.DecimalField(db_column='ElMonsarf', max_digits=18, decimal_places=2, blank=True, null=True)
    mortagaaelmawarden = models.DecimalField(db_column='MortagaaElMawarden', max_digits=18, decimal_places=2, blank=True, null=True)
    qte_in_stock = models.DecimalField(db_column='QTE_IN_STOCK', max_digits=18, decimal_places=2, blank=True, null=True)
    cat = models.ForeignKey(TblCategories, models.DO_NOTHING, db_column='CAT_ID', blank=True, null=True)
    cat_name = models.CharField(db_column='CAT_Name', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    unit = models.ForeignKey('TblUnitsSpareparts', models.DO_NOTHING, db_column='Unit_ID', blank=True, null=True)
    unit_name = models.CharField(db_column='Unit_Name', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    minimum_threshold = models.DecimalField(db_column='Minimum_Threshold', max_digits=18, decimal_places=2, blank=True, null=True)
    maximum_threshold = models.DecimalField(db_column='Maximum_Threshold', max_digits=18, decimal_places=2, blank=True, null=True)
    image_product = models.BinaryField(db_column='Image_Product', blank=True, null=True)
    unit_price = models.DecimalField(db_column='Unit_Price', max_digits=18, decimal_places=2, blank=True, null=True)
    location = models.CharField(db_column='Location', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)
    expiry_warning = models.CharField(db_column='Expiry_Warning', max_length=10, db_collation='Arabic_CI_AS', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Tbl_Products'

class TblInvoices(models.Model):
    invoice_id = models.IntegerField(db_column='Invoice_ID')
    invoice_number = models.CharField(db_column='Invoice_Number', primary_key=True, max_length=255, db_collation='Arabic_CI_AS')
    invoice_date = models.DateField(db_column='Invoice_Date', blank=True, null=True)
    invoice_type = models.CharField(db_column='Invoice_Type', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    numberofitems = models.IntegerField(db_column='NumberOfItems', blank=True, null=True)
    recipient = models.CharField(db_column='Recipient', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    supplier_id = models.IntegerField(db_column='Supplier_ID', blank=True, null=True)
    customer_id = models.IntegerField(db_column='Customer_ID', blank=True, null=True)
    customer_invoice_number = models.CharField(db_column='Customer_Invoice_Number', max_length=255, db_collation='Arabic_CI_AS', blank=True, null=True)
    supplier_invoice_number = models.CharField(db_column='Supplier_Invoice_Number', max_length=255, db_collation='Arabic_CI_AS', blank=True, null=True)
    total_invoice_value = models.DecimalField(db_column='Total_Invoice_Value', max_digits=18, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Tbl_Invoices'

class TblInvoiceitems(models.Model):
    invoice_code_programing = models.AutoField(db_column='Invoice_Code_Programing', primary_key=True)
    invoice_id = models.IntegerField(db_column='Invoice_ID', blank=True, null=True)
    invoice_number = models.CharField(db_column='Invoice_Number', max_length=255, db_collation='Arabic_CI_AS', blank=True, null=True)
    product = models.ForeignKey(TblProducts, models.DO_NOTHING, db_column='Product_ID', blank=True, null=True)
    product_name = models.CharField(db_column='Product_Name', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    quantity_elwarad = models.DecimalField(db_column='Quantity_ElWarad', max_digits=18, decimal_places=2, blank=True, null=True)
    quantity_elmonsarf = models.DecimalField(db_column='Quantity_ElMonsarf', max_digits=18, decimal_places=2, blank=True, null=True)
    quantity_mortagaaelmawarden = models.DecimalField(db_column='Quantity_MortagaaElMawarden', max_digits=18, decimal_places=2, blank=True, null=True)
    quantity_mortagaaomalaa = models.DecimalField(db_column='Quantity_MortagaaOmalaa', max_digits=18, decimal_places=2, blank=True, null=True)
    unit_id = models.IntegerField(db_column='Unit_ID', blank=True, null=True)
    unit_price = models.DecimalField(db_column='Unit_Price', max_digits=18, decimal_places=2, blank=True, null=True)
    invoice_date = models.DateField(db_column='Invoice_Date', blank=True, null=True)
    invoice_type = models.CharField(db_column='Invoice_Type', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    recipient = models.CharField(db_column='Recipient', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    received_machine = models.CharField(db_column='Received_Machine', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    machine_unit = models.CharField(db_column='Machine_Unit', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    returninvoicenumber = models.CharField(db_column='ReturnInvoiceNumber', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    total_invoice_value = models.DecimalField(db_column='Total_Invoice_Value', max_digits=18, decimal_places=2, blank=True, null=True)
    balance_time_entry = models.DecimalField(db_column='Balance_Time_Entry', max_digits=18, decimal_places=2, blank=True, null=True)
    data_entry_date = models.DateField(db_column='Data_Entry_Date', blank=True, null=True)
    data_entry_by = models.CharField(db_column='Data_Entry_By', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    notes = models.CharField(db_column='Notes', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Tbl_InvoiceItems'

class TblSuppliers(models.Model):
    supplier_id = models.IntegerField(db_column='Supplier_ID', primary_key=True)
    supplier_name = models.CharField(db_column='Supplier_Name', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Tbl_Suppliers'

class TblUnitsSpareparts(models.Model):
    unit_id = models.IntegerField(db_column='Unit_ID', primary_key=True)
    unit_name = models.CharField(db_column='Unit_Name', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Tbl_Units_SpareParts'

class SystemSettings(models.Model):
    LANGUAGE_CHOICES = [
        ('ar', 'العربية'),
        ('en', 'English'),
    ]

    FONT_CHOICES = [
        ('cairo', 'Cairo'),
        ('tajawal', 'Tajawal'),
        ('almarai', 'Almarai'),
        ('ibm-plex-sans-arabic', 'IBM Plex Sans Arabic'),
        ('noto-sans-arabic', 'Noto Sans Arabic'),
    ]

    DIRECTION_CHOICES = [
        ('rtl', 'من اليمين إلى اليسار'),
        ('ltr', 'من اليسار إلى اليمين'),
    ]

    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='ar',
        verbose_name=_('لغة النظام')
    )

    font_family = models.CharField(
        max_length=50,
        choices=FONT_CHOICES,
        default='cairo',
        verbose_name=_('الخط المستخدم')
    )

    text_direction = models.CharField(
        max_length=3,
        choices=DIRECTION_CHOICES,
        default='rtl',
        verbose_name=_('اتجاه النص')
    )

    class Meta:
        verbose_name = _('إعدادات النظام')
        verbose_name_plural = _('إعدادات النظام')

    def __str__(self):
        return f"System Settings - {self.language} - {self.font_family}"

    @classmethod
    def get_settings(cls):
        settings = cls.objects.first()
        if not settings:
            settings = cls.objects.create()
        return settings