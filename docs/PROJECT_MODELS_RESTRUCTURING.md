# إعادة هيكلة نماذج المشاريع والمهام الموحدة
# Unified Project and Task Models Restructuring

## نظرة عامة | Overview

تم إعادة هيكلة نماذج المشاريع والمهام في نظام الدولية لتوفير نظام موحد ومتكامل لإدارة المشاريع والمهام والاجتماعات. هذا التحديث يدمج الوظائف المتفرقة في نظام شامل ومنظم.

This document describes the restructuring of project and task models in the ElDawliya system to provide a unified and integrated system for managing projects, tasks, and meetings.

## الهيكل الجديد | New Structure

### النماذج الأساسية | Core Models

#### 1. ProjectCategory (تصنيفات المشاريع)
```python
class ProjectCategory(BaseModel):
    name = CharField(max_length=100, unique=True)
    description = TextField(blank=True, null=True)
    color = CharField(max_length=7, default='#3498db')
    icon = CharField(max_length=50, default='fas fa-project-diagram')
    parent = ForeignKey('self', null=True, blank=True)
```

**الميزات:**
- تصنيف هرمي للمشاريع
- ألوان وأيقونات مخصصة
- دعم التصنيفات الفرعية

#### 2. Project (المشاريع)
```python
class Project(AuditableModel, SoftDeleteModel):
    name = CharField(max_length=200)
    code = CharField(max_length=20, unique=True)
    description = TextField()
    category = ForeignKey(ProjectCategory)
    status = CharField(choices=STATUS_CHOICES)
    priority = CharField(choices=PRIORITY_CHOICES)
    start_date = DateField()
    end_date = DateField()
    actual_end_date = DateField(null=True, blank=True)
    budget = DecimalField(max_digits=15, decimal_places=2)
    actual_cost = DecimalField(max_digits=15, decimal_places=2)
    progress_percentage = PositiveIntegerField(default=0)
    manager = ForeignKey(User)
    team_members = ManyToManyField(User, through='ProjectMember')
    parent_project = ForeignKey('self', null=True, blank=True)
```

**الحالات المتاحة:**
- `planning`: تخطيط
- `active`: نشط
- `on_hold`: معلق
- `completed`: مكتمل
- `cancelled`: ملغي
- `archived`: مؤرشف

**الأولويات:**
- `low`: منخفضة
- `medium`: متوسطة
- `high`: عالية
- `critical`: حرجة

#### 3. ProjectPhase (مراحل المشروع)
```python
class ProjectPhase(AuditableModel):
    project = ForeignKey(Project)
    name = CharField(max_length=200)
    description = TextField(blank=True, null=True)
    order = PositiveIntegerField(default=1)
    status = CharField(choices=STATUS_CHOICES)
    start_date = DateField()
    end_date = DateField()
    actual_end_date = DateField(null=True, blank=True)
    progress_percentage = PositiveIntegerField(default=0)
    budget = DecimalField(max_digits=15, decimal_places=2)
    actual_cost = DecimalField(max_digits=15, decimal_places=2)
    responsible_person = ForeignKey(User)
```

#### 4. ProjectMilestone (معالم المشروع)
```python
class ProjectMilestone(AuditableModel):
    project = ForeignKey(Project)
    phase = ForeignKey(ProjectPhase, null=True, blank=True)
    name = CharField(max_length=200)
    description = TextField(blank=True, null=True)
    target_date = DateField()
    actual_date = DateField(null=True, blank=True)
    status = CharField(choices=STATUS_CHOICES)
    importance = PositiveIntegerField(default=5)
```

#### 5. ProjectMember (أعضاء فريق المشروع)
```python
class ProjectMember(BaseModel):
    project = ForeignKey(Project)
    user = ForeignKey(User)
    role = CharField(choices=ROLE_CHOICES)
    joined_date = DateField(default=timezone.now)
    left_date = DateField(null=True, blank=True)
    hourly_rate = DecimalField(max_digits=10, decimal_places=2)
    permissions = ManyToManyField(Permission)
```

**الأدوار المتاحة:**
- `manager`: مدير المشروع
- `lead`: قائد الفريق
- `developer`: مطور
- `analyst`: محلل
- `designer`: مصمم
- `tester`: مختبر
- `consultant`: استشاري
- `stakeholder`: صاحب مصلحة
- `observer`: مراقب

### نماذج المهام | Task Models

#### 6. Task (المهام الموحدة)
```python
class Task(AuditableModel, SoftDeleteModel):
    title = CharField(max_length=200)
    description = TextField()
    task_type = CharField(choices=TYPE_CHOICES)
    project = ForeignKey(Project, null=True, blank=True)
    phase = ForeignKey(ProjectPhase, null=True, blank=True)
    milestone = ForeignKey(ProjectMilestone, null=True, blank=True)
    parent_task = ForeignKey('self', null=True, blank=True)
    assigned_to = ForeignKey(User)
    status = CharField(choices=STATUS_CHOICES)
    priority = CharField(choices=PRIORITY_CHOICES)
    start_date = DateTimeField()
    due_date = DateTimeField()
    completed_date = DateTimeField(null=True, blank=True)
    estimated_hours = DecimalField(max_digits=8, decimal_places=2)
    actual_hours = DecimalField(max_digits=8, decimal_places=2)
    progress_percentage = PositiveIntegerField(default=0)
    is_private = BooleanField(default=False)
    tags = CharField(max_length=500, blank=True, null=True)
```

**أنواع المهام:**
- `regular`: مهمة عادية
- `meeting`: مهمة اجتماع
- `milestone`: مهمة معلم
- `phase`: مهمة مرحلة

**حالات المهام:**
- `pending`: قيد الانتظار
- `in_progress`: قيد التنفيذ
- `completed`: مكتملة
- `cancelled`: ملغاة
- `deferred`: مؤجلة
- `blocked`: محجوبة

#### 7. TaskStep (خطوات المهام)
```python
class TaskStep(BaseModel):
    task = ForeignKey(Task)
    description = TextField()
    notes = TextField(blank=True, null=True)
    completed = BooleanField(default=False)
    completion_date = DateTimeField(null=True, blank=True)
    hours_spent = DecimalField(max_digits=8, decimal_places=2)
```

#### 8. TimeEntry (إدخالات الوقت)
```python
class TimeEntry(BaseModel):
    task = ForeignKey(Task)
    user = ForeignKey(User)
    start_time = DateTimeField()
    end_time = DateTimeField(null=True, blank=True)
    duration_hours = DecimalField(max_digits=8, decimal_places=2)
    description = TextField(blank=True, null=True)
    is_billable = BooleanField(default=True)
```

### نماذج الاجتماعات | Meeting Models

#### 9. Meeting (الاجتماعات المحسنة)
```python
class Meeting(AuditableModel):
    title = CharField(max_length=200)
    description = TextField(blank=True, null=True)
    meeting_type = CharField(choices=TYPE_CHOICES)
    project = ForeignKey(Project, null=True, blank=True)
    start_datetime = DateTimeField()
    end_datetime = DateTimeField()
    location = CharField(max_length=200, blank=True, null=True)
    virtual_link = URLField(blank=True, null=True)
    status = CharField(choices=STATUS_CHOICES)
    organizer = ForeignKey(User)
    attendees = ManyToManyField(User, through='MeetingAttendee')
    agenda = TextField(blank=True, null=True)
    minutes = TextField(blank=True, null=True)
```

**أنواع الاجتماعات:**
- `project`: اجتماع مشروع
- `team`: اجتماع فريق
- `client`: اجتماع عميل
- `review`: اجتماع مراجعة
- `planning`: اجتماع تخطيط
- `standup`: اجتماع يومي
- `other`: أخرى

#### 10. MeetingAttendee (حضور الاجتماعات)
```python
class MeetingAttendee(BaseModel):
    meeting = ForeignKey(Meeting)
    user = ForeignKey(User)
    role = CharField(choices=ROLE_CHOICES)
    attendance_status = CharField(choices=ATTENDANCE_STATUS_CHOICES)
    response_date = DateTimeField(null=True, blank=True)
    notes = TextField(blank=True, null=True)
```

**حالات الحضور:**
- `invited`: مدعو
- `accepted`: قبل
- `declined`: رفض
- `tentative`: مؤقت
- `attended`: حضر
- `absent`: غائب

### نماذج الوثائق | Document Models

#### 11. Document (إدارة الوثائق والملفات)
```python
class Document(AuditableModel, SoftDeleteModel):
    name = CharField(max_length=200)
    description = TextField(blank=True, null=True)
    document_type = CharField(choices=DOCUMENT_TYPE_CHOICES)
    file = FileField(upload_to='documents/%Y/%m/')
    file_size = PositiveIntegerField(null=True, blank=True)
    mime_type = CharField(max_length=100, blank=True, null=True)
    project = ForeignKey(Project, null=True, blank=True)
    task = ForeignKey(Task, null=True, blank=True)
    meeting = ForeignKey(Meeting, null=True, blank=True)
    version = CharField(max_length=20, default='1.0')
    is_confidential = BooleanField(default=False)
    tags = CharField(max_length=500, blank=True, null=True)
```

**أنواع الوثائق:**
- `project_doc`: وثيقة مشروع
- `meeting_doc`: وثيقة اجتماع
- `task_doc`: وثيقة مهمة
- `contract`: عقد
- `specification`: مواصفات
- `report`: تقرير
- `presentation`: عرض تقديمي
- `image`: صورة
- `other`: أخرى

## الميزات الجديدة | New Features

### 1. النظام الهرمي | Hierarchical System
- مشاريع فرعية (Subprojects)
- مهام فرعية (Subtasks)
- تصنيفات هرمية (Hierarchical Categories)

### 2. تتبع الوقت المتقدم | Advanced Time Tracking
- إدخالات الوقت التفصيلية
- تتبع الساعات المقدرة مقابل الفعلية
- تقارير الإنتاجية

### 3. إدارة الوثائق | Document Management
- ربط الوثائق بالمشاريع والمهام والاجتماعات
- إدارة الإصدارات
- تصنيف الوثائق السرية

### 4. نظام الصلاحيات المتقدم | Advanced Permissions
- صلاحيات على مستوى المشروع
- أدوار مخصصة لأعضاء الفريق
- صلاحيات الوثائق السرية

### 5. التكامل الموحد | Unified Integration
- ربط المهام بالاجتماعات
- ربط المعالم بالمراحل
- تتبع التقدم الشامل

## قاعدة البيانات | Database Structure

### الجداول الجديدة | New Tables
```sql
-- Project Tables
project_categories
projects
project_phases
project_milestones
project_members

-- Task Tables
tasks
task_steps
time_entries

-- Meeting Tables
meetings
meeting_attendees

-- Document Tables
documents
```

### الفهارس المحسنة | Optimized Indexes
```sql
-- Performance Indexes
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_manager ON projects(manager_id);
CREATE INDEX idx_tasks_status_assigned_to ON tasks(status, assigned_to_id);
CREATE INDEX idx_tasks_project_status ON tasks(project_id, status);
CREATE INDEX idx_meetings_start_datetime ON meetings(start_datetime);
CREATE INDEX idx_time_entries_task_user ON time_entries(task_id, user_id);
```

## الهجرة | Migration

### سكريبت الهجرة | Migration Script
تم إنشاء سكريبت شامل لهجرة البيانات من النماذج القديمة:

```bash
python manage.py migrate_project_models --dry-run
python manage.py migrate_project_models
```

### خطوات الهجرة | Migration Steps
1. **إنشاء التصنيفات الافتراضية**
   - مشاريع عامة
   - مهام إدارية
   - اجتماعات

2. **إنشاء المشاريع الافتراضية**
   - مشروع للمهام العامة
   - مشروع للمهام الإدارية
   - مشروع للاجتماعات

3. **هجرة المهام الموجودة**
   - تحويل المهام القديمة إلى النموذج الجديد
   - ربط المهام بالمشاريع الافتراضية

4. **هجرة خطوات المهام**
   - تحويل خطوات المهام القديمة

5. **هجرة الاجتماعات**
   - تحويل الاجتماعات القديمة
   - ربط الاجتماعات بمشروع الاجتماعات

6. **هجرة حضور الاجتماعات**
   - تحويل سجلات الحضور

7. **هجرة مهام الاجتماعات**
   - تحويل مهام الاجتماعات إلى مهام عادية

## التحقق والاختبار | Validation and Testing

### سكريبتات التحقق | Validation Scripts
```bash
# التحقق من صحة الصيغة
python scripts/test_project_models_syntax.py

# التحقق من هيكل النماذج
python scripts/validate_project_models.py
```

### الاختبارات المتضمنة | Included Tests
- التحقق من صحة الصيغة
- التحقق من هيكل النماذج
- التحقق من العلاقات
- التحقق من قواعد التحقق
- التحقق من الطرق والخصائص
- التحقق من هيكل قاعدة البيانات
- التحقق من الصلاحيات
- التحقق من الخيارات

## الاستخدام | Usage

### إنشاء مشروع جديد | Creating a New Project
```python
from core.models.projects import Project, ProjectCategory

category = ProjectCategory.objects.get(name='مشاريع عامة')
project = Project.objects.create(
    name='مشروع تطوير النظام',
    code='DEV001',
    description='مشروع تطوير وتحسين النظام',
    category=category,
    status='planning',
    priority='high',
    start_date=date.today(),
    end_date=date.today() + timedelta(days=90),
    manager=user
)
```

### إنشاء مهمة جديدة | Creating a New Task
```python
from core.models.projects import Task

task = Task.objects.create(
    title='تطوير واجهة المستخدم',
    description='تطوير واجهة المستخدم للوحة التحكم',
    task_type='regular',
    project=project,
    assigned_to=developer,
    status='pending',
    priority='high',
    start_date=timezone.now(),
    due_date=timezone.now() + timedelta(days=14),
    estimated_hours=40
)
```

### إنشاء اجتماع جديد | Creating a New Meeting
```python
from core.models.projects import Meeting

meeting = Meeting.objects.create(
    title='اجتماع مراجعة المشروع',
    description='مراجعة تقدم المشروع والخطوات التالية',
    meeting_type='project',
    project=project,
    start_datetime=timezone.now() + timedelta(days=1),
    end_datetime=timezone.now() + timedelta(days=1, hours=1),
    organizer=manager,
    status='scheduled'
)
```

## الفوائد | Benefits

### 1. التوحيد والتكامل | Unification and Integration
- نظام موحد لإدارة المشاريع والمهام
- تكامل كامل بين المكونات المختلفة
- تقليل التكرار والتعقيد

### 2. المرونة والقابلية للتوسع | Flexibility and Scalability
- هيكل هرمي قابل للتوسع
- دعم المشاريع المعقدة
- إمكانية التخصيص المتقدم

### 3. تحسين الأداء | Performance Improvement
- فهارس محسنة لقاعدة البيانات
- استعلامات محسنة
- تخزين مؤقت ذكي

### 4. سهولة الاستخدام | Ease of Use
- واجهة موحدة للمستخدمين
- تجربة مستخدم محسنة
- تقارير شاملة

### 5. الأمان والصلاحيات | Security and Permissions
- نظام صلاحيات متقدم
- حماية الوثائق السرية
- تدقيق شامل للعمليات

## الخطوات التالية | Next Steps

1. **تطبيق الهجرة** - تشغيل سكريبت الهجرة على بيانات الإنتاج
2. **تطوير الواجهات** - إنشاء واجهات المستخدم للنماذج الجديدة
3. **تطوير APIs** - إنشاء واجهات برمجة التطبيقات
4. **التدريب** - تدريب المستخدمين على النظام الجديد
5. **المراقبة والتحسين** - مراقبة الأداء والتحسين المستمر

## الخلاصة | Conclusion

إعادة هيكلة نماذج المشاريع والمهام تمثل تحسيناً جوهرياً في نظام الدولية، حيث توفر نظاماً موحداً ومتكاملاً لإدارة المشاريع والمهام والاجتماعات. هذا التحديث يحسن من الأداء والمرونة وسهولة الاستخدام، مما يجعل النظام أكثر فعالية وقابلية للتوسع.

The restructuring of project and task models represents a fundamental improvement in the ElDawliya system, providing a unified and integrated system for managing projects, tasks, and meetings. This update improves performance, flexibility, and usability, making the system more effective and scalable.