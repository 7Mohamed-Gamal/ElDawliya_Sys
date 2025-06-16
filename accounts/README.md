# تطبيق إدارة الحسابات (Accounts Application)

## نظرة عامة (Application Overview)

تطبيق إدارة الحسابات هو المسؤول عن إدارة المستخدمين والمصادقة والصلاحيات في نظام الدولية. يوفر نظام تسجيل دخول آمن وإدارة شاملة للمستخدمين مع دعم كامل للغة العربية.

**الغرض الرئيسي**: إدارة المستخدمين والمصادقة والصلاحيات مع واجهة عربية متكاملة.

## الميزات الرئيسية (Key Features)

### 1. نظام المصادقة (Authentication System)
- تسجيل دخول آمن
- تسجيل خروج
- إدارة جلسات المستخدمين
- حماية من هجمات CSRF

### 2. إدارة المستخدمين (User Management)
- إنشاء حسابات مستخدمين جديدة
- تعديل بيانات المستخدمين
- إدارة الأدوار والصلاحيات
- تفعيل وإلغاء تفعيل الحسابات

### 3. نظام الأدوار (Role System)
- أدوار متعددة: مدير، مدير قسم، موظف
- صلاحيات مرنة حسب الدور
- تحكم في الوصول للوحدات

### 4. لوحة التحكم (Dashboard)
- إحصائيات المستخدمين
- الأنشطة الحديثة
- روابط سريعة للوحدات

## هيكل النماذج (Models Documentation)

### Users_Login_New (المستخدم)
```python
class Users_Login_New(AbstractUser):
    # الحقول الأساسية من AbstractUser
    username = models.CharField(max_length=150, unique=True)    # اسم المستخدم
    first_name = models.CharField(max_length=150)               # الاسم الأول
    last_name = models.CharField(max_length=150)                # الاسم الأخير
    email = models.EmailField()                                 # البريد الإلكتروني
    is_active = models.BooleanField(default=True)               # نشط
    is_staff = models.BooleanField(default=False)               # موظف إداري
    is_superuser = models.BooleanField(default=False)           # مدير عام
    date_joined = models.DateTimeField(auto_now_add=True)       # تاريخ الانضمام
    
    # الحقول المخصصة
    Role = models.CharField(max_length=20, choices=[
        ('admin', 'مدير'),
        ('manager', 'مدير قسم'), 
        ('employee', 'موظف')
    ])                                                          # الدور
    
    # خاصية للتوافق مع الكود القديم
    @property
    def IsActive(self):
        return self.is_active
```

### خصائص النموذج (Model Properties)
- **التوافق مع Django**: يستخدم AbstractUser للاستفادة من ميزات Django المدمجة
- **نظام الأدوار**: دعم ثلاثة أدوار رئيسية
- **المرونة**: إمكانية إضافة حقول جديدة بسهولة
- **الأمان**: استخدام نظام صلاحيات Django المدمج

## العروض (Views Documentation)

### عروض المصادقة (Authentication Views)

#### login_view
```python
def login_view(request):
    """عرض تسجيل الدخول"""
    # معالجة نموذج تسجيل الدخول
    # التحقق من بيانات المستخدم
    # إنشاء جلسة المستخدم
    # إعادة توجيه للصفحة المناسبة
```

#### logout_view
```python
def logout_view(request):
    """عرض تسجيل الخروج"""
    # إنهاء جلسة المستخدم
    # تنظيف البيانات المؤقتة
    # إعادة توجيه لصفحة تسجيل الدخول
```

### عروض إدارة المستخدمين (User Management Views)

#### dashboard_view
```python
@login_required
def dashboard_view(request):
    """لوحة تحكم إدارة المستخدمين"""
    # إحصائيات المستخدمين
    # عدد المستخدمين حسب الدور
    # المستخدمين النشطين
    # الأنشطة الحديثة
```

#### create_user_view
```python
@login_required
def create_user_view(request):
    """إنشاء مستخدم جديد"""
    # نموذج إنشاء المستخدم
    # تعيين الصلاحيات
    # إضافة للمجموعات
    # إرسال تنبيه
```

#### home_view
```python
@login_required
def home_view(request):
    """الصفحة الرئيسية للنظام"""
    # عرض وحدات النظام
    # الإحصائيات العامة
    # الروابط السريعة
    # التنبيهات
```

### عروض الصلاحيات (Permission Views)

#### edit_permissions_view
```python
@login_required
def edit_permissions_view(request, user_id):
    """تعديل صلاحيات المستخدم"""
    # عرض الصلاحيات الحالية
    # تعديل الصلاحيات
    # حفظ التغييرات
    # تسجيل العملية
```

#### access_denied
```python
def access_denied(request):
    """صفحة رفض الوصول"""
    # عرض رسالة عدم وجود صلاحية
    # تسجيل محاولة الوصول
    # إعادة توجيه مناسبة
```

## النماذج (Forms Documentation)

### CustomUserLoginForm
```python
class CustomUserLoginForm(AuthenticationForm):
    """نموذج تسجيل الدخول المخصص"""
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسم المستخدم'
        })
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور'
        })
    )
```

### CustomUserCreationForm
```python
class CustomUserCreationForm(UserCreationForm):
    """نموذج إنشاء المستخدم المخصص"""
    # الحقول الأساسية
    username = forms.CharField(label='اسم المستخدم')
    first_name = forms.CharField(label='الاسم الأول')
    last_name = forms.CharField(label='الاسم الأخير')
    email = forms.EmailField(label='البريد الإلكتروني')
    
    # الحقول المخصصة
    Role = forms.ChoiceField(
        label='الدور',
        choices=[('admin', 'مدير'), ('employee', 'موظف')]
    )
    is_active = forms.BooleanField(label='نشط')
    is_staff = forms.BooleanField(label='موظف إداري')
    
    # كلمات المرور
    password1 = forms.CharField(label='كلمة المرور')
    password2 = forms.CharField(label='تأكيد كلمة المرور')
```

## هيكل URLs (URL Patterns)

### المسارات الأساسية (Basic Routes)
```
/accounts/login/                    - تسجيل الدخول
/accounts/logout/                   - تسجيل الخروج
/accounts/dashboard/                - لوحة تحكم المستخدمين
/accounts/home/                     - الصفحة الرئيسية
/accounts/create-user/              - إنشاء مستخدم جديد
/accounts/edit-permissions/<id>/    - تعديل صلاحيات المستخدم
/accounts/access-denied/            - رفض الوصول
```

### تسمية المسارات (URL Naming)
```python
app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('home/', views.home_view, name='home'),
    path('create-user/', views.create_user_view, name='create_user'),
    path('edit-permissions/<int:user_id>/', views.edit_permissions_view, name='edit_permissions'),
    path('access-denied/', views.access_denied, name='access_denied'),
]
```

## القوالب (Templates)

### هيكل القوالب (Template Structure)
```
accounts/templates/accounts/
├── login.html                      # صفحة تسجيل الدخول
├── dashboard.html                  # لوحة تحكم المستخدمين
├── home.html                       # الصفحة الرئيسية
├── edit_permissions.html           # تعديل الصلاحيات
└── access_denied.html              # رفض الوصول
```

### ميزات القوالب (Template Features)
- **تصميم متجاوب**: Bootstrap 5 RTL
- **دعم العربية**: خطوط عربية وتخطيط RTL
- **أمان**: حماية CSRF في جميع النماذج
- **تفاعلية**: JavaScript للتحسينات
- **إمكانية الوصول**: معايير WCAG

### قالب تسجيل الدخول (Login Template)
```html
<!-- login.html -->
<div class="login-container">
    <div class="login-card">
        <div class="login-header">
            <h2>نظام شركة الدولية إنترناشونال</h2>
        </div>
        <div class="login-body">
            <form method="post">
                {% csrf_token %}
                <!-- حقول النموذج -->
                <button type="submit">تسجيل الدخول</button>
            </form>
        </div>
    </div>
</div>
```

## إدارة Django (Django Admin)

### CustomUserAdmin
```python
class CustomUserAdmin(UserAdmin):
    """إدارة المستخدمين المخصصة"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'Role', 'is_active']
    list_filter = ['Role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    fieldsets = UserAdmin.fieldsets + (
        ('معلومات إضافية', {'fields': ('Role',)}),
    )
```

### PermissionAdmin
```python
class PermissionAdmin(admin.ModelAdmin):
    """إدارة الصلاحيات"""
    list_display = ['name', 'content_type', 'codename']
    list_filter = ['content_type']
    search_fields = ['name', 'codename']
    
    def has_add_permission(self, request):
        return False  # منع إضافة صلاحيات يدوياً
```

## التبعيات (Dependencies)

### التبعيات الداخلية (Internal Dependencies)
- `administrator`: إعدادات النظام والصلاحيات
- `Hr`: ربط المستخدمين بالموظفين
- `audit`: تسجيل عمليات المستخدمين

### التبعيات الخارجية (External Dependencies)
- Django 5.0+ (نظام المصادقة المدمج)
- django-widget-tweaks (تحسين النماذج)

## الأمان (Security)

### إجراءات الأمان المطبقة
1. **حماية CSRF**: في جميع النماذج
2. **تشفير كلمات المرور**: باستخدام Django المدمج
3. **جلسات آمنة**: إعدادات جلسات محسنة
4. **تسجيل العمليات**: تتبع جميع عمليات المستخدمين
5. **التحقق من الصلاحيات**: في كل عرض

### أفضل الممارسات الأمنية
- استخدام HTTPS في الإنتاج
- تحديث كلمات المرور بانتظام
- مراقبة محاولات تسجيل الدخول الفاشلة
- تطبيق سياسات كلمات المرور القوية

## التكامل مع التطبيقات الأخرى (Integration)

### التكامل مع Hr
```python
# ربط المستخدم بالموظف
employee = Employee.objects.get(user=request.user)
```

### التكامل مع audit
```python
# تسجيل عمليات المستخدم
AuditLog.objects.create(
    user=request.user,
    action='LOGIN',
    ip_address=get_client_ip(request)
)
```

## أمثلة الاستخدام (Usage Examples)

### إنشاء مستخدم جديد
```python
from accounts.models import Users_Login_New

user = Users_Login_New.objects.create_user(
    username='ahmed.mohamed',
    email='ahmed@company.com',
    password='secure_password',
    first_name='أحمد',
    last_name='محمد',
    Role='employee'
)
```

### التحقق من الصلاحيات
```python
from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.Role == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_only_view(request):
    # عرض للمديرين فقط
    pass
```

### تسجيل الدخول برمجياً
```python
from django.contrib.auth import authenticate, login

user = authenticate(username='ahmed.mohamed', password='password')
if user is not None:
    login(request, user)
```

## الصيانة والتطوير (Maintenance)

### مراقبة النظام
- مراقبة محاولات تسجيل الدخول
- تتبع المستخدمين النشطين
- مراجعة الصلاحيات دورياً

### التحديثات المستقبلية
- إضافة مصادقة ثنائية العامل
- تحسين واجهة المستخدم
- إضافة المزيد من الأدوار
- تطوير API للمصادقة

---

**تم إنشاء هذا التوثيق في**: 2025-06-16  
**الإصدار**: 1.0  
**المطور**: فريق تطوير نظام الدولية
