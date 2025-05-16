# ملف forms.py لتطبيق المخزون
from django import forms
from django.utils.translation import gettext_lazy as _
from .models_local import (
    Category, Product, Supplier, Customer,
    Voucher, VoucherItem, LocalSystemSettings, Unit,
    Department, PurchaseRequest
)
from .models import TblInvoices as Invoice, TblInvoiceitems as InvoiceItem

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name', 'symbol']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'symbol': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProductForm(forms.ModelForm):
    # حقول لإنشاء تصنيف جديد
    new_category = forms.CharField(required=False, label="إضافة تصنيف جديد", widget=forms.HiddenInput())
    new_category_name = forms.CharField(required=False, label="اسم التصنيف الجديد", widget=forms.TextInput(attrs={'class': 'form-control'}))
    new_category_description = forms.CharField(required=False, label="وصف التصنيف الجديد", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    # حقول لإنشاء وحدة قياس جديدة
    new_unit = forms.CharField(required=False, label="إضافة وحدة قياس جديدة", widget=forms.HiddenInput())
    new_unit_name = forms.CharField(required=False, label="اسم الوحدة الجديدة", widget=forms.HiddenInput())
    new_unit_symbol = forms.CharField(required=False, label="رمز الوحدة الجديدة", widget=forms.HiddenInput())

    # حقل للتأكد من إرسال النموذج
    form_submitted = forms.CharField(required=False, widget=forms.HiddenInput(), initial='true')

    class Meta:
        model = Product
        fields = ['product_id', 'name', 'category', 'unit', 'initial_quantity', 'quantity', 'unit_price', 'minimum_threshold', 'maximum_threshold', 'location', 'description', 'image']
        widgets = {
            'product_id': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'initial_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'value': '0'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'value': '0'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'value': '0'}),
            'minimum_threshold': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'value': '0'}),
            'maximum_threshold': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'value': '0'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # جعل الحقول الأساسية إلزامية
        self.fields['product_id'].required = True
        self.fields['name'].required = True

        # جعل الحقول الأخرى غير إلزامية
        self.fields['category'].required = False
        self.fields['unit'].required = False
        self.fields['initial_quantity'].required = False
        self.fields['quantity'].required = False

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DepartmentForm(forms.ModelForm):
    # إضافة حقول وهمية للنموذج (لن يتم حفظها في قاعدة البيانات)
    code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label=_("كود القسم")
    )
    manager = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_("مدير القسم")
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_("الموقع")
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label=_("ملاحظات")
    )

    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # إذا كان هناك قسم موجود، قم بتعيين قيمة الكود
            self.initial['code'] = self.instance.code
        else:
            # إذا كان قسم جديد، اعرض رسالة أنه سيتم إنشاء الكود تلقائيًا
            self.initial['code'] = 'سيتم إنشاؤه تلقائيًا'

class VoucherForm(forms.ModelForm):
    class Meta:
        model = Voucher
        fields = ['voucher_number', 'voucher_type', 'date', 'supplier', 'department', 'customer', 'supplier_voucher_number', 'recipient', 'notes']
        widgets = {
            'voucher_number': forms.TextInput(attrs={'class': 'form-control'}),
            'voucher_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'supplier_voucher_number': forms.TextInput(attrs={'class': 'form-control'}),
            'recipient': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields conditionally required based on voucher type
        self.fields['supplier'].required = False
        self.fields['department'].required = False
        self.fields['customer'].required = False
        self.fields['supplier_voucher_number'].required = False
        self.fields['recipient'].required = False

        if 'instance' in kwargs and kwargs['instance']:
            voucher_type = kwargs['instance'].voucher_type
        elif 'initial' in kwargs and 'voucher_type' in kwargs['initial']:
            voucher_type = kwargs['initial']['voucher_type']
        else:
            voucher_type = None

        if voucher_type:
            self.set_required_fields(voucher_type)

    def set_required_fields(self, voucher_type):
        if voucher_type == 'إذن اضافة' or voucher_type == 'إذن مرتجع مورد':
            self.fields['supplier'].required = True
            self.fields['supplier_voucher_number'].required = True
        elif voucher_type == 'إذن صرف':
            self.fields['department'].required = True
            self.fields['recipient'].required = True
        elif voucher_type == 'اذن مرتجع عميل':
            self.fields['customer'].required = True

class VoucherItemForm(forms.ModelForm):
    class Meta:
        model = VoucherItem
        fields = ['voucher', 'product', 'quantity_added', 'quantity_disbursed', 'machine', 'machine_unit', 'unit_price']
        widgets = {
            'voucher': forms.Select(attrs={'class': 'form-select'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity_added': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'quantity_disbursed': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'machine': forms.TextInput(attrs={'class': 'form-control'}),
            'machine_unit': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields conditionally required based on voucher type
        self.fields['quantity_added'].required = False
        self.fields['quantity_disbursed'].required = False
        self.fields['machine'].required = False
        self.fields['machine_unit'].required = False

        if 'instance' in kwargs and kwargs['instance'] and kwargs['instance'].voucher:
            voucher_type = kwargs['instance'].voucher.voucher_type
            self.set_required_fields(voucher_type)

    def set_required_fields(self, voucher_type):
        if voucher_type == 'إذن اضافة' or voucher_type == 'اذن مرتجع عميل':
            self.fields['quantity_added'].required = True
            self.fields['quantity_disbursed'].required = False
            self.fields['machine'].required = False
            self.fields['machine_unit'].required = False
        elif voucher_type == 'إذن صرف':
            self.fields['quantity_added'].required = False
            self.fields['quantity_disbursed'].required = True
            self.fields['machine'].required = True
            self.fields['machine_unit'].required = True
        elif voucher_type == 'إذن مرتجع مورد':
            self.fields['quantity_added'].required = False
            self.fields['quantity_disbursed'].required = True
            self.fields['machine'].required = False
            self.fields['machine_unit'].required = False

class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ['product', 'status']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class LocalSystemSettingsForm(forms.ModelForm):
    class Meta:
        model = LocalSystemSettings
        fields = [
            # معلومات الشركة
            'company_name', 'company_logo', 'company_address', 'company_phone', 'company_email',
            # إعدادات واجهة المستخدم
            'primary_color', 'secondary_color', 'items_per_page', 'compact_tables', 'currency',
            # إعدادات المخزون
            'enable_stock_alerts', 'default_min_stock_percentage',
            # إعدادات الفواتير
            'invoice_in_prefix', 'invoice_out_prefix', 'prevent_editing_completed_invoices'
        ]
        widgets = {
            # معلومات الشركة
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'company_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'company_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'company_email': forms.EmailInput(attrs={'class': 'form-control'}),

            # إعدادات واجهة المستخدم
            'primary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'items_per_page': forms.Select(attrs={'class': 'form-select'}, choices=[
                (10, '10'),
                (25, '25'),
                (50, '50'),
                (100, '100'),
            ]),
            'compact_tables': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'currency': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('EGP', 'جنيه مصري (ج.م)'),
                ('USD', 'دولار أمريكي ($)'),
                ('EUR', 'يورو (€)'),
                ('SAR', 'ريال سعودي (ر.س)'),
            ]),

            # إعدادات المخزون
            'enable_stock_alerts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'default_min_stock_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),

            # إعدادات الفواتير
            'invoice_in_prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_out_prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'prevent_editing_completed_invoices': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'invoice_date', 'invoice_type', 'recipient', 'supplier_id', 'customer_id', 'supplier_invoice_number', 'customer_invoice_number']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'invoice_type': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('إضافة', 'إضافة'),
                ('صرف', 'صرف'),
                ('مرتجع عميل', 'مرتجع عميل'),
                ('مرتجع مورد', 'مرتجع مورد'),
            ]),
            'recipient': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'customer_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'supplier_invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['invoice_number', 'product', 'quantity_elwarad', 'quantity_elmonsarf', 'quantity_mortagaaelmawarden', 'quantity_mortagaaomalaa', 'unit_price', 'received_machine', 'machine_unit']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity_elwarad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'quantity_elmonsarf': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'quantity_mortagaaelmawarden': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'quantity_mortagaaomalaa': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'received_machine': forms.TextInput(attrs={'class': 'form-control'}),
            'machine_unit': forms.TextInput(attrs={'class': 'form-control'}),
        }
