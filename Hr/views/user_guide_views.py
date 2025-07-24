"""
دليل المستخدم لنظام الموارد البشرية

هذا الملف يحتوي على واجهات عرض دليل المستخدم
وتوثيق نظام الموارد البشرية المتكامل
"""

from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _

class UserGuideBaseView(LoginRequiredMixin, TemplateView):
    """
    الصنف الأساسي لصفحات دليل المستخدم
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guide_sections'] = [
            {
                'id': 'overview',
                'title': _('نظرة عامة على النظام'),
                'icon': 'fa-tachometer-alt',
                'subsections': [
                    {'id': 'introduction', 'title': _('مقدمة')},
                    {'id': 'features', 'title': _('الميزات الرئيسية')},
                    {'id': 'navigation', 'title': _('التنقل في النظام')},
                ]
            },
            {
                'id': 'employee',
                'title': _('إدارة الموظفين'),
                'icon': 'fa-users',
                'subsections': [
                    {'id': 'employee-list', 'title': _('قائمة الموظفين')},
                    {'id': 'employee-add', 'title': _('إضافة موظف جديد')},
                    {'id': 'employee-profile', 'title': _('ملف الموظف')},
                    {'id': 'employee-documents', 'title': _('وثائق الموظف')},
                ]
            },
            {
                'id': 'organization',
                'title': _('الهيكل التنظيمي'),
                'icon': 'fa-sitemap',
                'subsections': [
                    {'id': 'departments', 'title': _('الأقسام')},
                    {'id': 'positions', 'title': _('المناصب الوظيفية')},
                    {'id': 'locations', 'title': _('المواقع والفروع')},
                ]
            },
            {
                'id': 'attendance',
                'title': _('نظام الحضور والانصراف'),
                'icon': 'fa-clock',
                'subsections': [
                    {'id': 'attendance-record', 'title': _('تسجيل الحضور')},
                    {'id': 'attendance-report', 'title': _('تقارير الحضور')},
                    {'id': 'shifts', 'title': _('إدارة الورديات')},
                    {'id': 'overtime', 'title': _('العمل الإضافي')},
                ]
            },
            {
                'id': 'leave',
                'title': _('نظام الإجازات'),
                'icon': 'fa-calendar-alt',
                'subsections': [
                    {'id': 'leave-request', 'title': _('طلب إجازة')},
                    {'id': 'leave-approval', 'title': _('الموافقة على الإجازات')},
                    {'id': 'leave-balance', 'title': _('رصيد الإجازات')},
                    {'id': 'leave-types', 'title': _('أنواع الإجازات')},
                ]
            },
            {
                'id': 'payroll',
                'title': _('نظام الرواتب'),
                'icon': 'fa-money-bill-wave',
                'subsections': [
                    {'id': 'salary-structure', 'title': _('هيكل الرواتب')},
                    {'id': 'payroll-generation', 'title': _('إنشاء كشف الراتب')},
                    {'id': 'payroll-approval', 'title': _('اعتماد كشوف الرواتب')},
                    {'id': 'payslips', 'title': _('قسائم الرواتب')},
                ]
            },
            {
                'id': 'reports',
                'title': _('التقارير والإحصائيات'),
                'icon': 'fa-chart-bar',
                'subsections': [
                    {'id': 'standard-reports', 'title': _('التقارير القياسية')},
                    {'id': 'advanced-reports', 'title': _('التقارير المتقدمة')},
                    {'id': 'kpi-dashboard', 'title': _('لوحة مؤشرات الأداء')},
                ]
            },
            {
                'id': 'settings',
                'title': _('إعدادات النظام'),
                'icon': 'fa-cogs',
                'subsections': [
                    {'id': 'company-settings', 'title': _('إعدادات الشركة')},
                    {'id': 'user-management', 'title': _('إدارة المستخدمين')},
                    {'id': 'permissions', 'title': _('الصلاحيات والأدوار')},
                    {'id': 'workflow', 'title': _('إعدادات سير العمل')},
                ]
            },
        ]

        # تحديد القسم النشط حالياً
        active_section = kwargs.get('section', 'overview')
        active_subsection = kwargs.get('subsection', None)

        if active_subsection is None and active_section in [s['id'] for s in context['guide_sections']]:
            # إذا لم يتم تحديد قسم فرعي، استخدم القسم الفرعي الأول في القسم النشط
            for section in context['guide_sections']:
                if section['id'] == active_section and section['subsections']:
                    active_subsection = section['subsections'][0]['id']
                    break

        context['active_section'] = active_section
        context['active_subsection'] = active_subsection

        return context


class UserGuideHomeView(UserGuideBaseView):
    """
    الصفحة الرئيسية لدليل المستخدم
    """
    template_name = 'hr/user_guide/user_guide_home.html'


class UserGuideSectionView(UserGuideBaseView):
    """
    صفحة قسم معين من دليل المستخدم
    """
    template_name = 'hr/user_guide/user_guide_section.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section_id = self.kwargs.get('section')
        subsection_id = self.kwargs.get('subsection', None)

        context['content'] = self.get_section_content(section_id, subsection_id)
        return context

    def get_section_content(self, section_id, subsection_id):
        """
        الحصول على محتوى القسم المطلوب
        يمكن توسيع هذه الدالة لجلب المحتوى من قاعدة البيانات أو ملفات خارجية
        """
        content = {}

        # معلومات أساسية عن القسم
        section_info = {
            'overview': {
                'title': _('نظرة عامة على النظام'),
                'description': _('دليل شامل للتعرف على نظام الموارد البشرية المتكامل وميزاته الرئيسية')
            },
            'employee': {
                'title': _('إدارة الموظفين'),
                'description': _('كيفية إدارة بيانات الموظفين وملفاتهم الشخصية')
            },
            'organization': {
                'title': _('الهيكل التنظيمي'),
                'description': _('إدارة الهيكل التنظيمي للشركة والأقسام والمناصب')
            },
            'attendance': {
                'title': _('نظام الحضور والانصراف'),
                'description': _('كيفية إدارة حضور وانصراف الموظفين والورديات')
            },
            'leave': {
                'title': _('نظام الإجازات'),
                'description': _('إدارة طلبات الإجازات وأرصدة الإجازات للموظفين')
            },
            'payroll': {
                'title': _('نظام الرواتب'),
                'description': _('إنشاء وإدارة كشوف الرواتب وحساب المستحقات')
            },
            'reports': {
                'title': _('التقارير والإحصائيات'),
                'description': _('استخراج وتحليل التقارير المختلفة من النظام')
            },
            'settings': {
                'title': _('إعدادات النظام'),
                'description': _('تخصيص وضبط إعدادات النظام والصلاحيات')
            },
        }

        # معلومات القسم الحالي
        if section_id in section_info:
            content['section_info'] = section_info[section_id]

        # محتوى الأقسام الفرعية
        subsections_content = {}

        # نظرة عامة
        if section_id == 'overview':
            subsections_content['introduction'] = {
                'title': _('مقدمة'),
                'content': """
                <p>مرحباً بك في نظام الموارد البشرية المتكامل من شركة الدولية. هذا النظام مصمم لتوفير حل شامل لإدارة جميع جوانب الموارد البشرية في مؤسستك، بدءاً من إدارة بيانات الموظفين وحتى حساب الرواتب وإدارة الأداء.</p>
                <p>تم تطوير النظام وفقاً لأحدث معايير تطوير البرمجيات وأفضل الممارسات في مجال الموارد البشرية، مع التركيز على سهولة الاستخدام والمرونة والأمان.</p>
                <h4>الفوائد الرئيسية للنظام</h4>
                <ul>
                    <li>توحيد جميع بيانات الموارد البشرية في منصة واحدة متكاملة</li>
                    <li>أتمتة العمليات اليدوية وتقليل الأخطاء البشرية</li>
                    <li>توفير الوقت والجهد في إدارة شؤون الموظفين</li>
                    <li>تحسين دقة وسرعة حساب الرواتب والمستحقات</li>
                    <li>تمكين الإدارة من اتخاذ القرارات بناءً على بيانات دقيقة وتقارير تحليلية</li>
                    <li>تعزيز الشفافية والتواصل بين الموظفين والإدارة</li>
                </ul>
                <p>يهدف هذا الدليل إلى مساعدتك في فهم واستخدام جميع ميزات النظام بكفاءة، وسيكون مرجعاً شاملاً لك في جميع مراحل استخدامك للنظام.</p>
                """
            }

            subsections_content['features'] = {
                'title': _('الميزات الرئيسية'),
                'content': """
                <h4>الميزات الرئيسية للنظام</h4>
                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title"><i class="fas fa-users mr-2 text-primary"></i>إدارة الموظفين</h5>
                                <ul>
                                    <li>إدارة شاملة لبيانات الموظفين</li>
                                    <li>ملفات شخصية متكاملة مع الوثائق</li>
                                    <li>متابعة تواريخ انتهاء العقود والوثائق</li>
                                    <li>إدارة التسلسل الهرمي والهيكل التنظيمي</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title"><i class="fas fa-clock mr-2 text-success"></i>نظام الحضور والانصراف</h5>
                                <ul>
                                    <li>تكامل مع أجهزة البصمة المختلفة</li>
                                    <li>إدارة الورديات والجداول المرنة</li>
                                    <li>احتساب العمل الإضافي والتأخير</li>
                                    <li>تقارير متقدمة للحضور والغياب</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title"><i class="fas fa-calendar-alt mr-2 text-info"></i>نظام الإجازات</h5>
                                <ul>
                                    <li>إدارة جميع أنواع الإجازات</li>
                                    <li>تتبع أرصدة الإجازات آلياً</li>
                                    <li>سير عمل للموافقة على طلبات الإجازات</li>
                                    <li>إشعارات آلية للطلبات والموافقات</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title"><i class="fas fa-money-bill-wave mr-2 text-warning"></i>نظام الرواتب</h5>
                                <ul>
                                    <li>إعداد هياكل رواتب متعددة</li>
                                    <li>احتساب آلي للرواتب والبدلات والاستقطاعات</li>
                                    <li>التكامل مع نظام الحضور والإجازات</li>
                                    <li>إنشاء وطباعة كشوف ومسيرات الرواتب</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title"><i class="fas fa-chart-bar mr-2 text-danger"></i>التقارير والتحليلات</h5>
                                <ul>
                                    <li>مؤشرات أداء رئيسية للموارد البشرية</li>
                                    <li>تقارير تحليلية متقدمة وقابلة للتخصيص</li>
                                    <li>لوحات معلومات تفاعلية</li>
                                    <li>تصدير التقارير بصيغ متعددة</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-body">
                                <h5 class="card-title"><i class="fas fa-shield-alt mr-2 text-dark"></i>الأمان والصلاحيات</h5>
                                <ul>
                                    <li>نظام صلاحيات متعدد المستويات</li>
                                    <li>أدوار مخصصة حسب احتياجات المؤسسة</li>
                                    <li>سجل تدقيق كامل للتغييرات</li>
                                    <li>تشفير للبيانات الحساسة</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                """
            }

            subsections_content['navigation'] = {
                'title': _('التنقل في النظام'),
                'content': """
                <h4>التنقل في النظام</h4>
                <p>يتميز النظام بواجهة مستخدم بديهية تسهل التنقل بين مختلف أقسام ووظائف النظام.</p>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">القائمة الرئيسية</h5>
                    </div>
                    <div class="card-body">
                        <p>تتوفر القائمة الرئيسية على الجانب اليمين من الشاشة وتحتوي على جميع الأقسام الرئيسية للنظام:</p>
                        <ul>
                            <li><strong>لوحة التحكم:</strong> نظرة عامة على مؤشرات الأداء الرئيسية</li>
                            <li><strong>الموظفين:</strong> إدارة بيانات الموظفين وملفاتهم الشخصية</li>
                            <li><strong>المؤسسة:</strong> إدارة الهيكل التنظيمي والأقسام والمناصب</li>
                            <li><strong>الحضور:</strong> تسجيل وإدارة الحضور والانصراف</li>
                            <li><strong>الإجازات:</strong> إدارة طلبات وأرصدة الإجازات</li>
                            <li><strong>الرواتب:</strong> إنشاء وإدارة كشوف الرواتب</li>
                            <li><strong>التقارير:</strong> عرض وتحليل مختلف التقارير</li>
                            <li><strong>الإعدادات:</strong> ضبط إعدادات النظام والصلاحيات</li>
                        </ul>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">شريط التنقل العلوي</h5>
                    </div>
                    <div class="card-body">
                        <p>يوفر شريط التنقل العلوي وصولاً سريعاً إلى:</p>
                        <ul>
                            <li><strong>الإشعارات:</strong> عرض آخر التنبيهات والإشعارات المهمة</li>
                            <li><strong>الرسائل:</strong> التواصل مع المستخدمين الآخرين</li>
                            <li><strong>البحث:</strong> البحث السريع في النظام</li>
                            <li><strong>حساب المستخدم:</strong> إدارة ملفك الشخصي وإعدادات الحساب</li>
                        </ul>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">الإجراءات الشائعة</h5>
                    </div>
                    <div class="card-body">
                        <p>في أغلب صفحات النظام، ستجد الإجراءات الشائعة متاحة من خلال:</p>
                        <ul>
                            <li><strong>أزرار الإجراءات:</strong> تظهر عادة في أعلى الصفحات (إضافة، تعديل، حذف، طباعة، تصدير)</li>
                            <li><strong>قائمة الإجراءات:</strong> قائمة منسدلة تحتوي على إجراءات إضافية متاحة للعنصر المحدد</li>
                            <li><strong>الرموز والأيقونات:</strong> تمثل اختصارات للإجراءات الشائعة (مثل تعديل، حذف، عرض التفاصيل)</li>
                        </ul>
                    </div>
                </div>

                <div class="alert alert-info">
                    <h5><i class="fas fa-lightbulb mr-2"></i>نصيحة</h5>
                    <p>يمكنك تخصيص القائمة المفضلة بإضافة العناصر الأكثر استخداماً لتسهيل الوصول إليها.</p>
                </div>
                """
            }
        }

        # إدارة الموظفين
        elif section_id == 'employee':
            subsections_content['employee-list'] = {
                'title': _('قائمة الموظفين'),
                'content': """
                <h4>قائمة الموظفين</h4>
                <p>توفر صفحة قائمة الموظفين عرضاً شاملاً لجميع الموظفين في المؤسسة مع إمكانية البحث والتصفية والفرز.</p>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">عرض قائمة الموظفين</h5>
                    </div>
                    <div class="card-body">
                        <p>للوصول إلى قائمة الموظفين:</p>
                        <ol>
                            <li>انقر على <strong>الموظفين</strong> في القائمة الرئيسية.</li>
                            <li>اختر <strong>قائمة الموظفين</strong> من القائمة الفرعية.</li>
                        </ol>
                        <p>ستظهر قائمة بجميع الموظفين مع معلوماتهم الأساسية مثل:</p>
                        <ul>
                            <li>الرقم الوظيفي</li>
                            <li>الاسم الكامل</li>
                            <li>القسم والمنصب الوظيفي</li>
                            <li>تاريخ التعيين</li>
                            <li>الحالة الوظيفية</li>
                        </ul>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">البحث والتصفية</h5>
                    </div>
                    <div class="card-body">
                        <p>يمكنك البحث عن موظف محدد أو تصفية القائمة باستخدام:</p>
                        <ul>
                            <li><strong>البحث السريع:</strong> أدخل اسم الموظف أو رقمه الوظيفي في مربع البحث.</li>
                            <li><strong>الفلاتر المتقدمة:</strong> استخدم خيارات الفلترة لتضييق النتائج حسب:
                                <ul>
                                    <li>القسم</li>
                                    <li>المنصب الوظيفي</li>
                                    <li>الحالة الوظيفية</li>
                                    <li>تاريخ التعيين</li>
                                </ul>
                            </li>
                        </ul>
                        <div class="alert alert-tip">
                            <strong>نصيحة:</strong> يمكنك حفظ إعدادات الفلترة المفضلة لاستخدامها لاحقاً.
                        </div>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">إجراءات متاحة</h5>
                    </div>
                    <div class="card-body">
                        <p>من قائمة الموظفين، يمكنك تنفيذ الإجراءات التالية:</p>
                        <ul>
                            <li><strong>عرض التفاصيل:</strong> انقر على اسم الموظف لعرض ملفه الشخصي الكامل.</li>
                            <li><strong>تعديل بيانات الموظف:</strong> انقر على أيقونة التعديل لتحديث بيانات الموظف.</li>
                            <li><strong>إجراءات إضافية:</strong> استخدم قائمة الإجراءات لـ:
                                <ul>
                                    <li>طباعة معلومات الموظف</li>
                                    <li>تغيير الحالة الوظيفية</li>
                                    <li>نقل إلى قسم آخر</li>
                                    <li>إرسال إشعار</li>
                                </ul>
                            </li>
                        </ul>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">تصدير البيانات</h5>
                    </div>
                    <div class="card-body">
                        <p>يمكنك تصدير قائمة الموظفين بصيغ مختلفة:</p>
                        <ol>
                            <li>انقر على زر <strong>تصدير</strong> في أعلى القائمة.</li>
                            <li>اختر الصيغة المطلوبة (Excel، PDF، CSV).</li>
                            <li>حدد الحقول التي ترغب بتضمينها في الملف المُصدّر.</li>
                            <li>انقر على <strong>تصدير</strong> لتنزيل الملف.</li>
                        </ol>
                    </div>
                </div>
                """
            }

            subsections_content['employee-add'] = {
                'title': _('إضافة موظف جديد'),
                'content': """
                <h4>إضافة موظف جديد</h4>
                <p>يوفر النظام عملية منظمة لإضافة موظف جديد وإدخال جميع البيانات المطلوبة.</p>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">بدء عملية إضافة موظف جديد</h5>
                    </div>
                    <div class="card-body">
                        <p>للبدء في إضافة موظف جديد:</p>
                        <ol>
                            <li>انتقل إلى <strong>الموظفين > قائمة الموظفين</strong>.</li>
                            <li>انقر على زر <strong>إضافة موظف</strong> في أعلى الصفحة.</li>
                            <li>ستظهر صفحة إدخال بيانات الموظف الجديد مقسمة إلى عدة أقسام.</li>
                        </ol>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">إدخال البيانات الأساسية</h5>
                    </div>
                    <div class="card-body">
                        <p>في القسم الأول، قم بإدخال البيانات الشخصية الأساسية للموظف:</p>
                        <ul>
                            <li><strong>الاسم الكامل:</strong> باللغتين العربية والإنجليزية</li>
                            <li><strong>الرقم الوظيفي:</strong> سيقترح النظام رقماً تلقائياً أو يمكنك تعيين رقم مخصص</li>
                            <li><strong>رقم الهوية/الإقامة:</strong> مع إمكانية إرفاق صورة</li>
                            <li><strong>تاريخ الميلاد:</strong> استخدم مربع اختيار التاريخ</li>
                            <li><strong>الجنس:</strong> ذكر أو أنثى</li>
                            <li><strong>الجنسية:</strong> اختر من القائمة المنسدلة</li>
                            <li><strong>الحالة الاجتماعية:</strong> اختر من القائمة المنسدلة</li>
                        </ul>
                        <div class="alert alert-warning">
                            <strong>مهم:</strong> الحقول المميزة بعلامة (*) هي حقول إلزامية ويجب إكمالها.
                        </div>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">بيانات التوظيف</h5>
                    </div>
                    <div class="card-body">
                        <p>في قسم بيانات التوظيف، أدخل معلومات الوظيفة:</p>
                        <ul>
                            <li><strong>القسم:</strong> اختر القسم من القائمة المنسدلة</li>
                            <li><strong>المنصب الوظيفي:</strong> سيتم تحديث القائمة بناءً على القسم المختار</li>
                            <li><strong>الدرجة الوظيفية:</strong> اختر من القائمة المنسدلة</li>
                            <li><strong>المدير المباشر:</strong> اختر من قائمة الموظفين</li>
                            <li><strong>تاريخ التعيين:</strong> تاريخ بدء العمل</li>
                            <li><strong>نوع التوظيف:</strong> دوام كامل، جزئي، عقد، إلخ</li>
                            <li><strong>فترة التجربة:</strong> حدد مدة فترة التجربة (بالأيام أو الأشهر)</li>
                        </ul>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">بيانات الاتصال</h5>
                    </div>
                    <div class="card-body">
                        <p>أدخل معلومات الاتصال بالموظف:</p>
                        <ul>
                            <li><strong>رقم الجوال الشخصي:</strong> مع رمز الدولة</li>
                            <li><strong>رقم الجوال العملي:</strong> إن وجد</li>
                            <li><strong>البريد الإلكتروني الشخصي:</strong> للتواصل الشخصي</li>
                            <li><strong>البريد الإلكتروني العملي:</strong> سيتم إنشاؤه تلقائياً أو يمكن إدخاله يدوياً</li>
                            <li><strong>العنوان:</strong> العنوان التفصيلي للموظف</li>
                            <li><strong>معلومات الاتصال في حالات الطوارئ:</strong>
                                <ul>
                                    <li>اسم جهة الاتصال</li>
                                    <li>صلة القرابة</li>
                                    <li>رقم الهاتف</li>
                                </ul>
                            </li>
                        </ul>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">بيانات الراتب والبنك</h5>
                    </div>
                    <div class="card-body">
                        <p>أدخل معلومات الراتب والحساب البنكي:</p>
                        <ul>
                            <li><strong>الراتب الأساسي:</strong> قيمة الراتب الأساسي</li>
                            <li><strong>هيكل الراتب:</strong> اختر من الهياكل المعرفة مسبقاً</li>
                            <li><strong>البنك:</strong> اسم البنك</li>
                            <li><strong>رقم الحساب:</strong> رقم الحساب البنكي</li>
                            <li><strong>رقم الآيبان:</strong> الرقم الدولي للحساب البنكي</li>
                        </ul>
                        <div class="alert alert-info">
                            <strong>ملاحظة:</strong> يمكن إضافة البدلات والمزايا الإضافية بعد حفظ بيانات الموظف.
                        </div>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">المرفقات والوثائق</h5>
                    </div>
                    <div class="card-body">
                        <p>يمكنك إرفاق المستندات المطلوبة للموظف:</p>
                        <ul>
                            <li><strong>صورة شخصية:</strong> يمكن التقاطها من الكاميرا أو رفعها من الجهاز</li>
                            <li><strong>الهوية الوطنية/الإقامة:</strong> صورة من الجهتين</li>
                            <li><strong>جواز السفر:</strong> مع صفحة التأشيرة إن وجدت</li>
                            <li><strong>الشهادات العلمية:</strong> مع إمكانية إضافة بيانات كل شهادة</li>
                            <li><strong>عقد العمل:</strong> نسخة من عقد العمل الموقع</li>
                            <li><strong>مستندات إضافية:</strong> أي مستندات أخرى مطلوبة</li>
                        </ul>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">حفظ بيانات الموظف</h5>
                    </div>
                    <div class="card-body">
                        <p>بعد إكمال جميع البيانات المطلوبة:</p>
                        <ol>
                            <li>انقر على زر <strong>حفظ</strong> لإضافة الموظف إلى النظام.</li>
                            <li>يمكنك النقر على <strong>حفظ ومتابعة</strong> للانتقال مباشرة إلى الخطوات التالية مثل:
                                <ul>
                                    <li>إضافة المزايا والبدلات</li>
                                    <li>تعيين الورديات وجدول العمل</li>
                                    <li>تحديد أرصدة الإجازات</li>
                                </ul>
                            </li>
                        </ol>
                        <div class="alert alert-success">
                            <strong>تلميح:</strong> يمكنك إنشاء قالب بيانات موظف لتسريع عملية إدخال البيانات للموظفين الذين لديهم معلومات متشابهة.
                        </div>
                    </div>
                </div>
                """
            }

            # يمكن إضافة المزيد من الأقسام الفرعية هنا للقسم "إدارة الموظفين"

        # يمكن إضافة محتوى لباقي الأقسام الرئيسية هنا

        # إذا تم تحديد قسم فرعي، قم بإرجاع محتواه
        if subsection_id and section_id in subsections_content and subsection_id in subsections_content:
            content['subsection'] = subsections_content[subsection_id]
        # وإلا قم بإرجاع جميع الأقسام الفرعية للقسم الرئيسي
        elif section_id in subsections_content:
            content['subsections'] = subsections_content

            # إذا لم يتم تحديد قسم فرعي، استخدم القسم الفرعي الأول
            if subsections_content:
                first_subsection_id = list(subsections_content.keys())[0]
                content['subsection'] = subsections_content[first_subsection_id]

        return content
