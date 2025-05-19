from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import Users_Login_New

User = get_user_model()

class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم المستخدم'})
    )
    password = forms.CharField(
        label='كلمة المرور', 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'أدخل كلمة المرور'})
    )


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم المستخدم'})
    )
    
    first_name = forms.CharField(
        label='الاسم الأول',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأول'})
    )
    
    last_name = forms.CharField(
        label='الاسم الأخير',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأخير'})
    )
    
    email = forms.EmailField(
        label='البريد الإلكتروني',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'})
    )
    
    Role = forms.ChoiceField(
        label='الدور',
        choices=[('admin', 'مدير'), ('employee', 'موظف')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_active = forms.BooleanField(
        label='نشط',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    is_staff = forms.BooleanField(
        label='موظف إداري',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    password1 = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'كلمة المرور'})
    )
    
    password2 = forms.CharField(
        label='تأكيد كلمة المرور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'تأكيد كلمة المرور'})
    )
    
    class Meta:
        model = Users_Login_New
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'Role', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        # تعيين صلاحيات المستخدم بناءً على الدور
        if self.cleaned_data.get('Role') == 'admin':
            user.is_staff = True
            user.is_superuser = True
        
        if commit:
            user.save()
        return user



