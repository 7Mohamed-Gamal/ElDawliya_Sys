"""
أمر إنشاء قوالب الإشعارات الافتراضية
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Hr.models_notifications import NotificationTemplate, NotificationRule


class Command(BaseCommand):
    help = 'إنشاء قوالب الإشعارات الافتراضية'
    
    def handle(self, *args, **options):
        self.stdout.write('إنشاء قوالب الإشعارات الافتراضية...')
        
        # قوالب الإشعارات
        templates = [
            {
                'name': 'إشعار موظف جديد',
                'code': 'employee_created',
                'description': 'إشعار عند إضافة موظف جديد',
                'notification_type': 'info',
                'title_template': 'مرحباً بالموظف الجديد: {{ employee.full_name }}',
                'message_template': 'تم إضافة موظف جديد {{ employee.full_name }} إلى قسم {{ employee.department.name }}. رقم الموظف: {{ employee.employee_number }}',
                'email_subject_template': 'موظف جديد - {{ employee.full_name }}',
                'email_body_template': '''
                <h2>مرحباً بالموظف الجديد</h2>
                <p>تم إضافة موظف جديد إلى النظام:</p>
                <ul>
                    <li><strong>الاسم:</strong> {{ employee.full_name }}</li>
                    <li><strong>رقم الموظف:</strong> {{ employee.employee_number }}</li>
                    <li><strong>القسم:</strong> {{ employee.department.name }}</li>
                    <li><strong>المنصب:</strong> {{ employee.job_title.title }}</li>
                    <li><strong>تاريخ التوظيف:</strong> {{ employee.hire_date }}</li>
                </ul>
                ''',
                'delivery_methods': ['email', 'in_app']
            },
            {
                'name': 'طلب إجازة جديد',
                'code': 'leave_requested',
                'description': 'إشعار عند تقديم طلب إجازة',
                'notification_type': 'info',
                'title_template': 'طلب إجازة جديد من {{ employee.full_name }}',
                'message_template': 'تم تقديم طلب إجازة {{ leave_type.name }} من {{ employee.full_name }} من {{ start_date }} إلى {{ end_date }}',
                'email_subject_template': 'طلب إجازة - {{ employee.full_name }}',
                'email_body_template': '''
                <h2>طلب إجازة جديد</h2>
                <p>تم تقديم طلب إجازة جديد:</p>
                <ul>
                    <li><strong>الموظف:</strong> {{ employee.full_name }}</li>
                    <li><strong>نوع الإجازة:</strong> {{ leave_type.name }}</li>
                    <li><strong>من تاريخ:</strong> {{ start_date }}</li>
                    <li><strong>إلى تاريخ:</strong> {{ end_date }}</li>
                    <li><strong>عدد الأيام:</strong> {{ days_count }}</li>
                    <li><strong>السبب:</strong> {{ reason }}</li>
                </ul>
                ''',
                'delivery_methods': ['email', 'in_app']
            },
            {
                'name': 'موافقة على الإجازة',
                'code': 'leave_approved',
                'description': 'إشعار عند الموافقة على الإجازة',
                'notification_type': 'success',
                'title_template': 'تم اعتماد طلب الإجازة',
                'message_template': 'تم اعتماد طلب إجازة {{ leave_type.name }} من {{ start_date }} إلى {{ end_date }}',
                'email_subject_template': 'تم اعتماد طلب الإجازة',
                'email_body_template': '''
                <h2>تم اعتماد طلب الإجازة</h2>
                <p>تم اعتماد طلب الإجازة الخاص بك:</p>
                <ul>
                    <li><strong>نوع الإجازة:</strong> {{ leave_type.name }}</li>
                    <li><strong>من تاريخ:</strong> {{ start_date }}</li>
                    <li><strong>إلى تاريخ:</strong> {{ end_date }}</li>
                    <li><strong>عدد الأيام:</strong> {{ days_count }}</li>
                    <li><strong>اعتمد بواسطة:</strong> {{ approved_by.full_name }}</li>
                </ul>
                ''',
                'delivery_methods': ['email', 'in_app', 'sms']
            },
            {
                'name': 'رفض الإجازة',
                'code': 'leave_rejected',
                'description': 'إشعار عند رفض الإجازة',
                'notification_type': 'warning',
                'title_template': 'تم رفض طلب الإجازة',
                'message_template': 'تم رفض طلب إجازة {{ leave_type.name }} من {{ start_date }} إلى {{ end_date }}. السبب: {{ rejection_reason }}',
                'email_subject_template': 'تم رفض طلب الإجازة',
                'email_body_template': '''
                <h2>تم رفض طلب الإجازة</h2>
                <p>تم رفض طلب الإجازة الخاص بك:</p>
                <ul>
                    <li><strong>نوع الإجازة:</strong> {{ leave_type.name }}</li>
                    <li><strong>من تاريخ:</strong> {{ start_date }}</li>
                    <li><strong>إلى تاريخ:</strong> {{ end_date }}</li>
                    <li><strong>سبب الرفض:</strong> {{ rejection_reason }}</li>
                    <li><strong>رفض بواسطة:</strong> {{ rejected_by.full_name }}</li>
                </ul>
                ''',
                'delivery_methods': ['email', 'in_app']
            },
            {
                'name': 'تأخير في الحضور',
                'code': 'attendance_late',
                'description': 'إشعار عند التأخير في الحضور',
                'notification_type': 'warning',
                'title_template': 'تأخير في الحضور - {{ employee.full_name }}',
                'message_template': 'تأخر الموظف {{ employee.full_name }} عن الحضور بـ {{ late_minutes }} دقيقة في {{ date }}',
                'email_subject_template': 'تأخير في الحضور - {{ employee.full_name }}',
                'email_body_template': '''
                <h2>تأخير في الحضور</h2>
                <p>تأخر الموظف عن الحضور:</p>
                <ul>
                    <li><strong>الموظف:</strong> {{ employee.full_name }}</li>
                    <li><strong>التاريخ:</strong> {{ date }}</li>
                    <li><strong>مدة التأخير:</strong> {{ late_minutes }} دقيقة</li>
                    <li><strong>وقت الحضور المتوقع:</strong> {{ expected_time }}</li>
                    <li><strong>وقت الحضور الفعلي:</strong> {{ actual_time }}</li>
                </ul>
                ''',
                'delivery_methods': ['email', 'in_app']
            },
            {
                'name': 'غياب بدون إذن',
                'code': 'attendance_absent',
                'description': 'إشعار عند الغياب بدون إذن',
                'notification_type': 'error',
                'title_template': 'غياب بدون إذن - {{ employee.full_name }}',
                'message_template': 'غاب الموظف {{ employee.full_name }} عن العمل بدون إذن في {{ date }}',
                'email_subject_template': 'غياب بدون إذن - {{ employee.full_name }}',
                'email_body_template': '''
                <h2>غياب بدون إذن</h2>
                <p>غاب الموظف عن العمل بدون إذن:</p>
                <ul>
                    <li><strong>الموظف:</strong> {{ employee.full_name }}</li>
                    <li><strong>التاريخ:</strong> {{ date }}</li>
                    <li><strong>القسم:</strong> {{ employee.department.name }}</li>
                    <li><strong>المدير المباشر:</strong> {{ employee.direct_manager.full_name }}</li>
                </ul>
                ''',
                'delivery_methods': ['email', 'in_app']
            },
            {
                'name': 'عيد ميلاد',
                'code': 'birthday',
                'description': 'تهنئة عيد الميلاد',
                'notification_type': 'success',
                'title_template': 'كل عام وأنت بخير {{ employee.full_name }}!',
                'message_template': 'نتمنى لك عيد ميلاد سعيد وعاماً مليئاً بالنجاح والإنجازات',
                'email_subject_template': 'كل عام وأنت بخير!',
                'email_body_template': '''
                <h2>🎉 كل عام وأنت بخير!</h2>
                <p>عزيزي/عزيزتي {{ employee.full_name }},</p>
                <p>نتمنى لك في عيد ميلادك كل الخير والسعادة، وعاماً جديداً مليئاً بالنجاح والإنجازات.</p>
                <p>شكراً لك على جهودك المتميزة وإسهامك في نجاح الشركة.</p>
                <p>مع أطيب التمنيات،<br>فريق الموارد البشرية</p>
                ''',
                'delivery_methods': ['email', 'in_app']
            },
            {
                'name': 'ذكرى التوظيف',
                'code': 'work_anniversary',
                'description': 'تهنئة ذكرى التوظيف',
                'notification_type': 'success',
                'title_template': 'ذكرى التوظيف - {{ service_years }} سنوات من العطاء',
                'message_template': 'تهانينا بمناسبة مرور {{ service_years }} سنوات على انضمامك للشركة',
                'email_subject_template': 'ذكرى التوظيف - {{ service_years }} سنوات',
                'email_body_template': '''
                <h2>🎊 ذكرى التوظيف</h2>
                <p>عزيزي/عزيزتي {{ employee.full_name }},</p>
                <p>تهانينا بمناسبة مرور {{ service_years }} سنوات على انضمامك لعائلة الشركة!</p>
                <p>خلال هذه السنوات، قدمت إسهامات قيمة وأظهرت التزاماً وتفانياً في العمل.</p>
                <p>نتطلع لسنوات أخرى من التعاون والنجاح المشترك.</p>
                <p>مع التقدير والامتنان،<br>إدارة الشركة</p>
                ''',
                'delivery_methods': ['email', 'in_app']
            },
            {
                'name': 'انتهاء صلاحية وثيقة',
                'code': 'document_expiring',
                'description': 'تنبيه انتهاء صلاحية الوثائق',
                'notification_type': 'warning',
                'title_template': 'تنبيه: انتهاء صلاحية {{ document.title }}',
                'message_template': 'ستنتهي صلاحية وثيقة {{ document.title }} خلال {{ days_until_expiry }} أيام',
                'email_subject_template': 'تنبيه: انتهاء صلاحية وثيقة',
                'email_body_template': '''
                <h2>⚠️ تنبيه انتهاء صلاحية وثيقة</h2>
                <p>ستنتهي صلاحية إحدى الوثائق قريباً:</p>
                <ul>
                    <li><strong>الوثيقة:</strong> {{ document.title }}</li>
                    <li><strong>الموظف:</strong> {{ employee.full_name }}</li>
                    <li><strong>تاريخ الانتهاء:</strong> {{ document.expiry_date }}</li>
                    <li><strong>الأيام المتبقية:</strong> {{ days_until_expiry }} يوم</li>
                </ul>
                <p>يرجى تجديد الوثيقة في أقرب وقت ممكن.</p>
                ''',
                'delivery_methods': ['email', 'in_app']
            },
            {
                'name': 'تذكير تقييم الأداء',
                'code': 'evaluation_due',
                'description': 'تذكير موعد تقييم الأداء',
                'notification_type': 'reminder',
                'title_template': 'تذكير: تقييم أداء {{ employee.full_name }}',
                'message_template': 'حان موعد تقييم أداء الموظف {{ employee.full_name }}. تاريخ الاستحقاق: {{ due_date }}',
                'email_subject_template': 'تذكير: تقييم الأداء',
                'email_body_template': '''
                <h2>📋 تذكير تقييم الأداء</h2>
                <p>حان موعد تقييم الأداء:</p>
                <ul>
                    <li><strong>الموظف:</strong> {{ employee.full_name }}</li>
                    <li><strong>القسم:</strong> {{ employee.department.name }}</li>
                    <li><strong>تاريخ الاستحقاق:</strong> {{ due_date }}</li>
                    <li><strong>نوع التقييم:</strong> {{ evaluation_type }}</li>
                </ul>
                <p>يرجى إكمال التقييم في الموعد المحدد.</p>
                ''',
                'delivery_methods': ['email', 'in_app']
            }
        ]
        
        created_count = 0
        
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                code=template_data['code'],
                defaults=template_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'تم إنشاء قالب: {template.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'القالب موجود بالفعل: {template.name}')
                )
        
        # إنشاء قواعد الإشعارات
        self._create_notification_rules()
        
        self.stdout.write(
            self.style.SUCCESS(f'تم إنشاء {created_count} قالب جديد')
        )
    
    def _create_notification_rules(self):
        """إنشاء قواعد الإشعارات الافتراضية"""
        
        rules = [
            {
                'name': 'إشعار موظف جديد للموارد البشرية',
                'description': 'إرسال إشعار لقسم الموارد البشرية عند إضافة موظف جديد',
                'trigger_event': 'employee_created',
                'template_code': 'employee_created',
                'recipient_roles': ['hr_department'],
                'conditions': {},
                'trigger_before_days': 0,
                'trigger_after_days': 0
            },
            {
                'name': 'إشعار طلب إجازة للمدير',
                'description': 'إرسال إشعار للمدير المباشر عند تقديم طلب إجازة',
                'trigger_event': 'leave_requested',
                'template_code': 'leave_requested',
                'recipient_roles': ['manager', 'hr_department'],
                'conditions': {},
                'trigger_before_days': 0,
                'trigger_after_days': 0
            },
            {
                'name': 'إشعار موافقة الإجازة للموظف',
                'description': 'إرسال إشعار للموظف عند الموافقة على الإجازة',
                'trigger_event': 'leave_approved',
                'template_code': 'leave_approved',
                'recipient_roles': ['employee'],
                'conditions': {},
                'trigger_before_days': 0,
                'trigger_after_days': 0
            },
            {
                'name': 'إشعار رفض الإجازة للموظف',
                'description': 'إرسال إشعار للموظف عند رفض الإجازة',
                'trigger_event': 'leave_rejected',
                'template_code': 'leave_rejected',
                'recipient_roles': ['employee'],
                'conditions': {},
                'trigger_before_days': 0,
                'trigger_after_days': 0
            },
            {
                'name': 'إشعار التأخير للمدير',
                'description': 'إرسال إشعار للمدير عند تأخير الموظف',
                'trigger_event': 'attendance_late',
                'template_code': 'attendance_late',
                'recipient_roles': ['manager'],
                'conditions': {'late_minutes': {'operator': 'gt', 'value': 15}},
                'trigger_before_days': 0,
                'trigger_after_days': 0
            },
            {
                'name': 'إشعار الغياب للموارد البشرية',
                'description': 'إرسال إشعار لقسم الموارد البشرية عند الغياب',
                'trigger_event': 'attendance_absent',
                'template_code': 'attendance_absent',
                'recipient_roles': ['manager', 'hr_department'],
                'conditions': {},
                'trigger_before_days': 0,
                'trigger_after_days': 0
            },
            {
                'name': 'تهنئة عيد الميلاد',
                'description': 'إرسال تهنئة عيد الميلاد للموظف',
                'trigger_event': 'birthday',
                'template_code': 'birthday',
                'recipient_roles': ['employee'],
                'conditions': {},
                'trigger_before_days': 0,
                'trigger_after_days': 0
            },
            {
                'name': 'تهنئة ذكرى التوظيف',
                'description': 'إرسال تهنئة ذكرى التوظيف للموظف',
                'trigger_event': 'work_anniversary',
                'template_code': 'work_anniversary',
                'recipient_roles': ['employee'],
                'conditions': {},
                'trigger_before_days': 0,
                'trigger_after_days': 0
            },
            {
                'name': 'تنبيه انتهاء صلاحية الوثائق',
                'description': 'تنبيه انتهاء صلاحية الوثائق قبل 30 يوم',
                'trigger_event': 'document_expiring',
                'template_code': 'document_expiring',
                'recipient_roles': ['employee', 'manager', 'hr_department'],
                'conditions': {},
                'trigger_before_days': 30,
                'trigger_after_days': 0
            },
            {
                'name': 'تذكير تقييم الأداء',
                'description': 'تذكير تقييم الأداء قبل 7 أيام',
                'trigger_event': 'evaluation_due',
                'template_code': 'evaluation_due',
                'recipient_roles': ['manager', 'hr_department'],
                'conditions': {},
                'trigger_before_days': 7,
                'trigger_after_days': 0
            }
        ]
        
        rules_created = 0
        
        for rule_data in rules:
            template_code = rule_data.pop('template_code')
            
            try:
                template = NotificationTemplate.objects.get(code=template_code)
                rule_data['template'] = template
                
                rule, created = NotificationRule.objects.get_or_create(
                    name=rule_data['name'],
                    defaults=rule_data
                )
                
                if created:
                    rules_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'تم إنشاء قاعدة: {rule.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'القاعدة موجودة بالفعل: {rule.name}')
                    )
                    
            except NotificationTemplate.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'القالب غير موجود: {template_code}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'تم إنشاء {rules_created} قاعدة جديدة')
        )