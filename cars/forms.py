from django import forms
from Hr.models.employee_model import Employee
from .models import Car, Trip, Settings, Supplier, RoutePoint

class SupplierForm(forms.ModelForm):
    """Form for adding and editing suppliers"""
    
    class Meta:
        model = Supplier
        fields = [
            'name',
            'contact_person',
            'phone',
            'email',
            'address'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }


class CarForm(forms.ModelForm):
    """Form for adding and editing cars"""
    
    class Meta:
        model = Car
        fields = [
            'car_code', 
            'car_name', 
            'car_type',
            'supplier',
            'distance_traveled', 
            'fuel_type', 
            'passengers_count', 
            'car_status',
            'fuel_consumption_rate'
        ]
        widgets = {
            'car_code': forms.TextInput(attrs={'class': 'form-control'}),
            'car_name': forms.TextInput(attrs={'class': 'form-control'}),
            'car_type': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'distance_traveled': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'passengers_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'car_status': forms.Select(attrs={'class': 'form-control'}),
            'fuel_consumption_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        }


class TripForm(forms.ModelForm):
    """Form for adding and editing trips"""
    
    class Meta:
        model = Trip
        fields = ['date', 'car', 'distance']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'car': forms.Select(attrs={'class': 'form-control'}),
            'distance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        }


class SettingsForm(forms.ModelForm):
    """Form for editing system settings"""
    
    class Meta:
        model = Settings
        fields = [
            'diesel_price', 
            'gasoline_price', 
            'gas_price', 
            'maintenance_rate', 
            'depreciation_rate', 
            'license_rate', 
            'driver_profit_rate', 
            'tax_rate'
        ]
        widgets = {
            'diesel_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'gasoline_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'gas_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'maintenance_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'depreciation_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'license_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'driver_profit_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        }


# EmployeeForm removed - using HR app's Employee model instead


class RoutePointForm(forms.ModelForm):
    """Form for adding and editing route points"""
    
    class Meta:
        model = RoutePoint
        fields = [
            'point_name',
            'departure_time',
            'employees'
        ]
        widgets = {
            'point_name': forms.TextInput(attrs={'class': 'form-control'}),
            'departure_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'employees': forms.SelectMultiple(attrs={'class': 'form-control'})
        }
