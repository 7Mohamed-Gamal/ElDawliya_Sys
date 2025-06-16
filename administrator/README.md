# تطبيق إدارة النظام (Administrator Application)

## نظرة عامة (Application Overview)

تطبيق إدارة النظام هو المسؤول عن إعدادات النظام العامة، إدارة قاعدة البيانات، نظام الصلاحيات المتقدم، وإدارة المستخدمين والمجموعات في نظام الدولية. يوفر واجهة شاملة لإدارة جميع جوانب النظام التقنية والإدارية.

**الغرض الرئيسي**: إدارة شاملة لإعدادات النظام والصلاحيات وقاعدة البيانات.

## الميزات الرئيسية (Key Features)

### 1. إعدادات النظام (System Settings)
- إعدادات قاعدة البيانات
- معلومات الشركة
- إعدادات اللغة والواجهة
- إعدادات الأمان
- إعدادات النسخ الاحتياطي

### 2. إدارة قاعدة البيانات (Database Management)
- إعداد اتصال قاعدة البيانات
- اختبار الاتصال
- إنشاء نسخ احتياطية
- استعادة النسخ الاحتياطية
- مراقبة الأداء

### 3. نظام الصلاحيات المتقدم (Advanced Permission System)
- إدارة الأقسام والوحدات
- صلاحيات مخصصة للمستخدمين
- مجموعات المستخدمين
- صلاحيات القوالب
- تحكم دقيق في الوصول

### 4. إدارة المستخدمين (User Management)
- إنشاء وتعديل المستخدمين
- إدارة المجموعات
- تعيين الصلاحيات
- مراقبة النشاط
- إدارة الجلسات

### 5. مراقبة النظام (System Monitoring)
- مراقبة الأداء
- سجلات النظام
- إحصائيات الاستخدام
- تنبيهات النظام
- تقارير الأمان

## هيكل النماذج (Models Documentation)

### SystemSettings (إعدادات النظام)
```python
class SystemSettings(models.Model):
    # إعدادات قاعدة البيانات
    db_host = models.CharField(max_length=255, default='localhost')    # خادم قاعدة البيانات
    db_name = models.CharField(max_length=255)                         # اسم قاعدة البيانات
    db_user = models.CharField(max_length=255)                         # مستخدم قاعدة البيانات
    db_password = models.CharField(max_length=255)                     # كلمة مرور قاعدة البيانات
    db_port = models.CharField(max_length=10, default='1433')          # منفذ قاعدة البيانات
    
    # معلومات الشركة
    company_name = models.CharField(max_length=255)                    # اسم الشركة
    company_address = models.TextField()                               # عنوان الشركة
    company_phone = models.CharField(max_length=50)                    # هاتف الشركة
    company_email = models.EmailField()                                # بريد الشركة
    company_website = models.URLField()                                # موقع الشركة
    company_logo = models.ImageField(upload_to='company/')             # شعار الشركة
    
    # إعدادات النظام
    system_name = models.CharField(max_length=255)                     # اسم النظام
    enable_debugging = models.BooleanField(default=False)              # تفعيل التصحيح
    maintenance_mode = models.BooleanField(default=False)              # وضع الصيانة
    timezone = models.CharField(max_length=50, default="Asia/Riyadh")  # المنطقة الزمنية
    date_format = models.CharField(max_length=50, default="Y-m-d")     # تنسيق التاريخ
    
    # إعدادات اللغة والواجهة
    language = models.CharField(max_length=10, default='ar')           # اللغة
    font_family = models.CharField(max_length=50, default='cairo')     # نوع الخط
    text_direction = models.CharField(max_length=10, default='rtl')    # اتجاه النص
```

### Department (القسم)
```python
class Department(models.Model):
    name = models.CharField(max_length=100)                            # اسم القسم
    description = models.TextField()                                   # وصف القسم
    icon = models.CharField(max_length=50)                             # أيقونة القسم
    color = models.CharField(max_length=20, default='#3498db')         # لون القسم
    is_active = models.BooleanField(default=True)                      # نشط
    order = models.IntegerField(default=0)                             # ترتيب العرض
    require_admin = models.BooleanField(default=False)                 # يتطلب صلاحيات المدير
    groups = models.ManyToManyField(Group, blank=True)                 # المجموعات المسموح لها
```

### Module (الوحدة)
```python
class Module(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE) # القسم
    name = models.CharField(max_length=100)                            # اسم الوحدة
    icon = models.CharField(max_length=50)                             # أيقونة الوحدة
    url = models.CharField(max_length=200)                             # رابط الوحدة
    description = models.CharField(max_length=255)                     # وصف الوحدة
    is_active = models.BooleanField(default=True)                      # نشط
    order = models.IntegerField(default=0)                             # ترتيب العرض
    bg_color = models.CharField(max_length=20, default='#3498db')      # لون الخلفية
    require_admin = models.BooleanField(default=False)                 # يتطلب صلاحيات المدير
    groups = models.ManyToManyField(Group, blank=True)                 # المجموعات المسموح لها
```

### UserGroup (مجموعة المستخدمين)
```python
class UserGroup(models.Model):
    name = models.CharField(max_length=100)                            # اسم المجموعة
    description = models.TextField()                                   # وصف المجموعة
    permissions = models.ManyToManyField(Permission)                   # الصلاحيات
    is_active = models.BooleanField(default=True)                      # نشط
    created_at = models.DateTimeField(auto_now_add=True)               # تاريخ الإنشاء
    updated_at = models.DateTimeField(auto_now=True)                   # تاريخ التحديث
```

### UserDepartmentPermission (صلاحيات القسم للمستخدم)
```python
class UserDepartmentPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)           # المستخدم
    department = models.ForeignKey(Department, on_delete=models.CASCADE) # القسم
    can_view = models.BooleanField(default=False)                      # يمكن العرض
    can_add = models.BooleanField(default=False)                       # يمكن الإضافة
    can_edit = models.BooleanField(default=False)                      # يمكن التعديل
    can_delete = models.BooleanField(default=False)                    # يمكن الحذف
    can_print = models.BooleanField(default=False)                     # يمكن الطباعة
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_dept_permissions') # منح بواسطة
    granted_at = models.DateTimeField(auto_now_add=True)               # تاريخ المنح
```

## العروض (Views Documentation)

### عروض لوحة التحكم (Dashboard Views)

#### admin_dashboard
```python
@login_required
@system_admin_required
def admin_dashboard(request):
    """لوحة تحكم مدير النظام"""
    # إحصائيات النظام
    # حالة قاعدة البيانات
    # المستخدمين النشطين
    # استخدام الموارد
    # التنبيهات
```

### عروض إعدادات النظام (System Settings Views)

#### system_settings
```python
@login_required
@system_admin_required
def system_settings(request):
    """إدارة إعدادات النظام"""
    # نموذج إعدادات النظام
    # حفظ الإعدادات
    # اختبار الإعدادات
    # إعادة تشغيل الخدمات
```

#### database_settings
```python
@login_required
@system_admin_required
def database_settings(request):
    """إعدادات قاعدة البيانات"""
    # إعدادات الاتصال
    # اختبار الاتصال
    # إحصائيات قاعدة البيانات
    # أدوات الصيانة
```

### عروض إدارة المستخدمين (User Management Views)

#### UserListView
```python
class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """عرض قائمة المستخدمين"""
    model = User
    template_name = 'administrator/user_list.html'
    permission_required = 'auth.view_user'
    
    def get_queryset(self):
        # فلترة المستخدمين
        # البحث والترتيب
        # تطبيق الصلاحيات
```

#### UserCreateView
```python
class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """إنشاء مستخدم جديد"""
    model = User
    form_class = UserCreationForm
    permission_required = 'auth.add_user'
    
    def form_valid(self, form):
        # حفظ المستخدم
        # تعيين الصلاحيات الافتراضية
        # إرسال إشعار
        # تسجيل العملية
```

### عروض إدارة الصلاحيات (Permission Management Views)

#### permission_dashboard
```python
@login_required
@system_admin_required
def permission_dashboard(request):
    """لوحة تحكم الصلاحيات"""
    # عرض الصلاحيات حسب المستخدم
    # عرض الصلاحيات حسب المجموعة
    # إحصائيات الصلاحيات
    # أدوات إدارة الصلاحيات
```

#### user_permissions
```python
@login_required
@system_admin_required
def user_permissions(request, pk):
    """إدارة صلاحيات المستخدم"""
    # عرض الصلاحيات الحالية
    # تعديل الصلاحيات
    # إضافة صلاحيات جديدة
    # حذف صلاحيات
```

## النماذج (Forms Documentation)

### SystemSettingsForm
```python
class SystemSettingsForm(forms.ModelForm):
    """نموذج إعدادات النظام"""
    class Meta:
        model = SystemSettings
        fields = '__all__'
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'db_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'enable_debugging': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'maintenance_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
```

### DatabaseConfigForm
```python
class DatabaseConfigForm(forms.Form):
    """نموذج إعداد قاعدة البيانات"""
    db_host = forms.CharField(
        label='خادم قاعدة البيانات',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    db_name = forms.CharField(
        label='اسم قاعدة البيانات',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    db_user = forms.CharField(
        label='اسم المستخدم',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    db_password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
```

### UserPermissionForm
```python
class UserPermissionForm(forms.Form):
    """نموذج صلاحيات المستخدم"""
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )
```

## هيكل URLs (URL Patterns)

### المسارات الرئيسية (Main Routes)
```
/administrator/                     - لوحة تحكم مدير النظام
/administrator/settings/            - إعدادات النظام
/administrator/database/            - إدارة قاعدة البيانات
/administrator/users/               - إدارة المستخدمين
/administrator/permissions/         - إدارة الصلاحيات
/administrator/groups/              - إدارة المجموعات
/administrator/departments/         - إدارة الأقسام
/administrator/modules/             - إدارة الوحدات
```

### مسارات قاعدة البيانات (Database Routes)
```
/administrator/database-setup/      - إعداد قاعدة البيانات
/administrator/test-connection/     - اختبار الاتصال
/administrator/backup/              - إنشاء نسخة احتياطية
/administrator/restore/             - استعادة نسخة احتياطية
/administrator/maintenance/         - صيانة قاعدة البيانات
```

### مسارات المستخدمين (User Routes)
```
/administrator/users/               - قائمة المستخدمين
/administrator/users/add/           - إضافة مستخدم
/administrator/users/<id>/          - تفاصيل المستخدم
/administrator/users/<id>/edit/     - تعديل المستخدم
/administrator/users/<id>/permissions/ - صلاحيات المستخدم
/administrator/users/<id>/groups/   - مجموعات المستخدم
```

## الأمان والصلاحيات (Security & Permissions)

### مستويات الأمان (Security Levels)
1. **مدير النظام**: وصول كامل لجميع الإعدادات
2. **مدير القسم**: وصول محدود للقسم المخصص
3. **المستخدم العادي**: وصول للوظائف الأساسية فقط

### إجراءات الأمان (Security Measures)
- تشفير كلمات المرور
- تسجيل جميع العمليات الحساسة
- جلسات آمنة مع انتهاء صلاحية
- حماية من هجمات CSRF
- تحديد معدل الطلبات

### نظام الصلاحيات المتقدم (Advanced Permission System)
```python
# فحص صلاحية القسم
@department_permission_required('hr', 'view')
def hr_dashboard(request):
    pass

# فحص صلاحية الوحدة
@module_permission_required('employees', 'add')
def create_employee(request):
    pass
```

## التكامل مع التطبيقات الأخرى (Integration)

### التكامل مع accounts
```python
# استخدام نظام المستخدمين المخصص
from accounts.models import Users_Login_New
```

### التكامل مع audit
```python
# تسجيل العمليات الإدارية
from audit.utils import log_admin_action

log_admin_action(
    user=request.user,
    action='SYSTEM_SETTINGS_UPDATE',
    details='تم تحديث إعدادات النظام'
)
```

## أمثلة الاستخدام (Usage Examples)

### إعداد النظام للمرة الأولى
```python
# إنشاء إعدادات النظام
settings = SystemSettings.objects.create(
    company_name='شركة الدولية إنترناشونال',
    system_name='نظام إدارة الموارد',
    db_host='localhost',
    db_name='eldawliya_db',
    language='ar',
    timezone='Asia/Riyadh'
)
```

### إنشاء مستخدم مدير
```python
from django.contrib.auth.models import User, Group

# إنشاء مجموعة المديرين
admin_group, created = Group.objects.get_or_create(name='مديرين النظام')

# إنشاء مستخدم مدير
admin_user = User.objects.create_user(
    username='admin',
    email='admin@company.com',
    password='secure_password',
    is_staff=True,
    is_superuser=True
)

admin_user.groups.add(admin_group)
```

### تعيين صلاحيات مخصصة
```python
from administrator.models import UserDepartmentPermission

# منح صلاحيات قسم الموارد البشرية
permission = UserDepartmentPermission.objects.create(
    user=user,
    department=Department.objects.get(name='الموارد البشرية'),
    can_view=True,
    can_add=True,
    can_edit=True,
    granted_by=request.user
)
```

---

**تم إنشاء هذا التوثيق في**: 2025-06-16  
**الإصدار**: 1.0  
**المطور**: فريق تطوير نظام الدولية
