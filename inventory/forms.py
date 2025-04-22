# inventory/forms.py
from django import forms
from .models_local import Category, Product, Supplier, Customer, Invoice, InvoiceItem, LocalSystemSettings

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'category', 'quantity', 'unit_price', 'minimum_threshold', 'maximum_threshold', 'location', 'description']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'contact_person', 'phone', 'email', 'address']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'invoice_type', 'date', 'supplier', 'customer', 'notes']

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['invoice', 'product', 'quantity', 'unit_price']

class LocalSystemSettingsForm(forms.ModelForm):
    class Meta:
        model = LocalSystemSettings
        fields = ['company_name', 'company_logo', 'company_address', 'company_phone', 'company_email']