from django import forms
from .models import PurchaseRequest, PurchaseRequestItem, Vendor

class PurchaseRequestForm(forms.ModelForm):
    """PurchaseRequestForm class"""
    class Meta:
        """Meta class"""
        model = PurchaseRequest
        fields = ['request_number', 'vendor', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
        }

class PurchaseRequestItemForm(forms.ModelForm):
    """PurchaseRequestItemForm class"""
    class Meta:
        """Meta class"""
        model = PurchaseRequestItem
        fields = ['product', 'quantity_requested', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class PurchaseRequestApprovalForm(forms.ModelForm):
    """PurchaseRequestApprovalForm class"""
    class Meta:
        """Meta class"""
        model = PurchaseRequest
        fields = ['status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }