# نظام مهام الموظفين (Employee Tasks System)

## نظرة عامة (Application Overview)

نظام مهام الموظفين هو تطبيق متكامل لإدارة مهام الموظفين في نظام الدولية. يوفر النظام واجهة احترافية لإدارة المهام الشخصية للموظفين، مع إمكانية تتبع خطوات المهام، وعرض المهام في تقويم، وتحليل أداء المهام.

**الغرض الرئيسي**: إدارة شاملة لمهام الموظفين الشخصية مع تتبع التقدم والإنتاجية.

## الميزات الرئيسية (Key Features)

### 1. إدارة المهام (Task Management)
- إنشاء وتعديل وحذف المهام الشخصية
- تصنيف المهام حسب الأولوية والحالة والتصنيف
- تتبع نسبة إنجاز المهام
- إمكانية إسناد المهام إلى موظفين آخرين
- خصوصية المهام (المهام الخاصة لا يراها إلا المنشئ والمشرف)

### 2. خطوات المهام (Task Steps)
- إضافة خطوات تفصيلية لكل مهمة
- تتبع حالة إنجاز كل خطوة
- تحديث نسبة إنجاز المهمة تلقائيًا بناءً على الخطوات المكتملة
- ترتيب الخطوات حسب الأولوية

### 3. التذكيرات (Reminders)
- إضافة تذكيرات للمهام
- تنبيهات للمهام المستحقة والمتأخرة
- تذكيرات قبل موعد الاستحقاق
- إشعارات فورية ومجدولة

### 4. التصنيفات (Categories)
- تصنيف المهام حسب النوع
- ألوان مميزة لكل تصنيف
- أيقونات مخصصة للتصنيفات
- فلترة المهام حسب التصنيف

### 5. التقويم والجدولة (Calendar & Scheduling)
- عرض المهام في تقويم شهري
- جدولة المهام حسب التواريخ
- عرض المهام المستحقة اليوم
- تنبيهات المواعيد النهائية

### 6. التقارير والتحليلات (Reports & Analytics)
- تقارير أداء المهام
- إحصائيات الإنتاجية
- تحليل الوقت المستغرق
- مقارنة الأداء بين الفترات

## هيكل النماذج (Models Documentation)

### TaskCategory (تصنيف المهام)
```python
class TaskCategory(models.Model):
    name = models.CharField(max_length=100)                            # اسم التصنيف
    description = models.TextField(blank=True)                         # وصف التصنيف
    color = models.CharField(max_length=7, default='#3498db')          # لون التصنيف (HEX)
    icon = models.CharField(max_length=50, default='fas fa-tasks')     # أيقونة التصنيف
    created_at = models.DateTimeField(auto_now_add=True)               # تاريخ الإنشاء
```

### EmployeeTask (مهمة الموظف)
```python
class EmployeeTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتملة'),
        ('cancelled', 'ملغية'),
        ('on_hold', 'معلقة'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'منخفضة'),
        ('medium', 'متوسطة'),
        ('high', 'عالية'),
        ('urgent', 'عاجلة'),
    ]

    title = models.CharField(max_length=200)                           # عنوان المهمة
    description = models.TextField()                                   # وصف المهمة
    category = models.ForeignKey(TaskCategory)                         # التصنيف
    created_by = models.ForeignKey(Users_Login_New)                    # منشئ المهمة
    assigned_to = models.ForeignKey(Users_Login_New)                   # المكلف بالمهمة
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)   # الحالة
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES) # الأولوية
    start_date = models.DateField()                                    # تاريخ البداية
    due_date = models.DateField()                                      # تاريخ الاستحقاق
    completion_date = models.DateField(null=True, blank=True)          # تاريخ الإنجاز
    progress = models.PositiveIntegerField(default=0)                  # نسبة الإنجاز (0-100)
    is_private = models.BooleanField(default=False)                    # مهمة خاصة
```

### TaskStep (خطوة المهمة)
```python
class TaskStep(models.Model):
    task = models.ForeignKey(EmployeeTask, related_name='steps')       # المهمة
    title = models.CharField(max_length=200)                           # عنوان الخطوة
    description = models.TextField(blank=True)                         # وصف الخطوة
    order = models.PositiveIntegerField(default=0)                     # ترتيب الخطوة
    is_completed = models.BooleanField(default=False)                  # مكتملة
    completed_at = models.DateTimeField(null=True, blank=True)         # تاريخ الإكمال
    created_by = models.ForeignKey(Users_Login_New)                    # منشئ الخطوة
```

### TaskReminder (تذكير المهمة)
```python
class TaskReminder(models.Model):
    REMINDER_TYPE_CHOICES = [
        ('email', 'بريد إلكتروني'),
        ('notification', 'إشعار'),
        ('sms', 'رسالة نصية'),
    ]

    task = models.ForeignKey(EmployeeTask, related_name='reminders')   # المهمة
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES) # نوع التذكير
    reminder_date = models.DateTimeField()                             # تاريخ التذكير
    message = models.TextField()                                       # رسالة التذكير
    is_sent = models.BooleanField(default=False)                       # تم الإرسال
    sent_at = models.DateTimeField(null=True, blank=True)              # تاريخ الإرسال
```

## العروض (Views Documentation)

### عروض لوحة التحكم (Dashboard Views)

#### dashboard
```python
@login_required
@employee_tasks_module_permission_required('dashboard', 'view')
def dashboard(request):
    """لوحة تحكم مهام الموظفين"""
    # إحصائيات المهام
    # المهام المستحقة اليوم
    # المهام المتأخرة
    # نسبة الإنجاز العامة
    # الرسوم البيانية
```

### عروض إدارة المهام (Task Management Views)

#### task_list
```python
@login_required
@employee_tasks_module_permission_required('tasks', 'view')
def task_list(request):
    """عرض قائمة المهام مع فلترة متقدمة"""
    # فلترة حسب الحالة
    # فلترة حسب الأولوية
    # فلترة حسب التصنيف
    # فلترة حسب التاريخ
    # البحث في العنوان والوصف
```

#### task_create
```python
@login_required
@employee_tasks_module_permission_required('tasks', 'add')
def task_create(request):
    """إنشاء مهمة جديدة"""
    # نموذج إنشاء المهمة
    # إضافة الخطوات
    # إضافة التذكيرات
    # تعيين المسؤول
```

#### task_detail
```python
@login_required
@can_access_task
def task_detail(request, pk):
    """عرض تفاصيل المهمة"""
    # تفاصيل المهمة
    # قائمة الخطوات
    # التذكيرات
    # سجل التحديثات
    # التعليقات
```

### عروض إدارة الخطوات (Step Management Views)

#### toggle_step_status
```python
@login_required
@can_access_task
def toggle_step_status(request, pk, step_id):
    """تغيير حالة الخطوة (مكتملة/غير مكتملة)"""
    # تحديث حالة الخطوة
    # إعادة حساب نسبة الإنجاز
    # تسجيل التحديث
    # إرسال إشعار
```

### عروض التقارير (Report Views)

#### analytics
```python
@login_required
@employee_tasks_module_permission_required('analytics', 'view')
def analytics(request):
    """تحليلات وتقارير المهام"""
    # تقرير الأداء الشهري
    # مقارنة الإنتاجية
    # تحليل الوقت
    # إحصائيات التصنيفات
```

## النماذج (Forms Documentation)

### EmployeeTaskForm
```python
class EmployeeTaskForm(forms.ModelForm):
    """نموذج إنشاء وتعديل مهام الموظفين"""
    class Meta:
        model = EmployeeTask
        fields = ['title', 'description', 'category', 'assigned_to', 'status',
                 'priority', 'start_date', 'due_date', 'progress', 'is_private']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
```

### TaskStepForm
```python
class TaskStepForm(forms.ModelForm):
    """نموذج إضافة خطوة للمهمة"""
    class Meta:
        model = TaskStep
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
```

### TaskFilterForm
```python
class TaskFilterForm(forms.Form):
    """نموذج فلترة المهام"""
    status = forms.ChoiceField(
        choices=[('', 'جميع الحالات')] + EmployeeTask.STATUS_CHOICES,
        required=False
    )
    priority = forms.ChoiceField(
        choices=[('', 'جميع الأولويات')] + EmployeeTask.PRIORITY_CHOICES,
        required=False
    )
    category = forms.ModelChoiceField(
        queryset=TaskCategory.objects.all(),
        required=False,
        empty_label='جميع التصنيفات'
    )
```

## هيكل URLs (URL Patterns)

### المسارات الرئيسية (Main Routes)
```
/employee-tasks/                    - لوحة التحكم الرئيسية
/employee-tasks/tasks/              - قائمة المهام
/employee-tasks/tasks/my/           - مهامي
/employee-tasks/tasks/assigned/     - المهام المكلف بها
/employee-tasks/tasks/create/       - إنشاء مهمة جديدة
/employee-tasks/categories/         - إدارة التصنيفات
/employee-tasks/calendar/           - عرض التقويم
/employee-tasks/analytics/          - التحليلات والتقارير
```

### مسارات المهام (Task Routes)
```
/employee-tasks/tasks/<id>/         - تفاصيل المهمة
/employee-tasks/tasks/<id>/edit/    - تعديل المهمة
/employee-tasks/tasks/<id>/delete/  - حذف المهمة
/employee-tasks/tasks/<id>/update-status/  - تحديث حالة المهمة
/employee-tasks/tasks/<id>/update-progress/  - تحديث نسبة الإنجاز
```

## نظام الصلاحيات (Permission System)

### الصلاحيات المخصصة (Custom Permissions)
```python
class Meta:
    permissions = [
        ("view_dashboard", "Can view employee tasks dashboard"),
        ("view_mytask", "Can view my employee tasks"),
        ("view_calendar", "Can view employee tasks calendar"),
        ("view_analytics", "Can view employee tasks analytics"),
        ("export_report", "Can export employee tasks reports"),
    ]
```

### التحكم في الوصول (Access Control)
- المنشئ يمكنه الوصول دائماً
- المكلف بالمهمة يمكنه الوصول
- المشرف يمكنه الوصول لجميع المهام
- المهام الخاصة محدودة الوصول

## التكامل مع التطبيقات الأخرى (Integration)

### التكامل مع accounts
```python
# ربط المهام بالمستخدمين
task = EmployeeTask.objects.create(
    created_by=request.user,
    assigned_to=selected_user
)
```

### التكامل مع notifications
```python
# إرسال إشعارات للمهام
Notification.objects.create(
    user=task.assigned_to,
    title=f'مهمة جديدة: {task.title}',
    message=task.description,
    notification_type='task_assigned'
)
```

## أمثلة الاستخدام (Usage Examples)

### إنشاء مهمة جديدة
```python
task = EmployeeTask.objects.create(
    title='مراجعة التقرير الشهري',
    description='مراجعة وتدقيق التقرير الشهري للقسم',
    category=TaskCategory.objects.get(name='إدارية'),
    created_by=request.user,
    assigned_to=request.user,
    priority='high',
    start_date=timezone.now().date(),
    due_date=timezone.now().date() + timedelta(days=3)
)
```

### تحديث نسبة الإنجاز
```python
def update_task_progress(task):
    """تحديث نسبة إنجاز المهمة بناءً على الخطوات المكتملة"""
    total_steps = task.steps.count()
    completed_steps = task.steps.filter(is_completed=True).count()

    if total_steps > 0:
        progress = (completed_steps / total_steps) * 100
        task.progress = round(progress)
        task.save()
```

---

**تم إنشاء هذا التوثيق في**: 2025-06-16
**الإصدار**: 1.0
**المطور**: فريق تطوير نظام الدولية
