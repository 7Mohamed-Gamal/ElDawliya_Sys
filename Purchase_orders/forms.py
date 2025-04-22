from django import forms
from .models import PurchaseRequest, PurchaseRequestItem

class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ['request_number', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class PurchaseRequestItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequestItem
        fields = ['product', 'quantity_requested', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class PurchaseRequestApprovalForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ['status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }