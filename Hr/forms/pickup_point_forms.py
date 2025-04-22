from django import forms
from django.utils.translation import gettext_lazy as _
from Hr.models.pickup_point_models import PickupPoint

class PickupPointForm(forms.ModelForm):
    class Meta:
        model = PickupPoint
        fields = ['name', 'address', 'coordinates', 'description', 'car', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'coordinates': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'car': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
