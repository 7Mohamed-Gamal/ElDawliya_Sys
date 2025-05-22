from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_models import Department, Job, JobInsurance, Car


class Employee(models.Model):
    MARITAL_STATUS_CHOICES = [
        ('أعزب', 'أعزب'),
        ('متزوج', 'متزوج'),
        ('مطلق', 'مطلق'),
        ('أرمل', 'أرمل'),
    ]
    
    EMP_TYPE_CHOICES = [
        ('ذكر', 'ذكر'),
        ('انثى', 'انثى'),
    ]
    
    WORKING_CONDITION_CHOICES = [
        ('سارى', 'سارى'),
        ('إجازة', 'إجازة'),
        ('استقالة', 'استقالة'),
        ('انقطاع عن العمل', 'انقطاع عن العمل'),
    ]
    
    INSURANCE_STATUS_CHOICES = [
        ('مؤمن عليه', 'مؤمن عليه'),
        ('غير مؤمن عليه', 'غير مؤمن عليه'),
    ]

    health_card_choices = [
        ('موجودة', 'موجودة'),
        ('غير موجوده', 'غير موجوده'),
    ]
    
    MILITARY_SERVICE_CHOICES = [
        ('أدى الخدمة', 'أدى الخدمة'),
        ('إعفاء', 'إعفاء'),
        ('مؤجل', 'مؤجل'),
        ('لم يبلغ السن', 'لم يبلغ السن'),
    ]
    
    SHIFT_TYPE_CHOICES = [
        ('صباحي', 'صباحي'),
        ('مسائي', 'مسائي'),
        ('ليلي', 'ليلي'),
    ]
    
    # Basic information
    emp_id = models.IntegerField(db_column='Emp_ID', primary_key=True, verbose_name=_("رقم الموظف"))
    emp_first_name = models.CharField(db_column='Emp_First_Name', max_length=50, null=True, blank=True, verbose_name=_("الاسم الأول"))
    emp_second_name = models.CharField(db_column='Emp_Second_Name', max_length=50, null=True, blank=True, verbose_name=_("الاسم الثاني"))
    emp_full_name = models.CharField(db_column='Emp_Full_Name', max_length=100, null=True, blank=True, verbose_name=_("الاسم الكامل"))
    emp_name_english = models.CharField(db_column='Emp_Name_English', max_length=50, null=True, blank=True, verbose_name=_("الاسم بالإنجليزية"))
    emp_type = models.CharField(db_column='Emp_Type', max_length=50, choices=EMP_TYPE_CHOICES, null=True, blank=True, verbose_name=_("نوع الموظف"))
    mother_name = models.CharField(db_column='Mother_Name', max_length=50, null=True, blank=True, verbose_name=_("اسم الأم"))
    
    # Contact information
    emp_phone1 = models.CharField(db_column='Emp_Phone1', max_length=50, null=True, blank=True, verbose_name=_("رقم الهاتف 1"))
    emp_phone2 = models.CharField(db_column='Emp_Phone2', max_length=50, null=True, blank=True, verbose_name=_("رقم الهاتف 2"))
    emp_address = models.CharField(db_column='Emp_Address', max_length=200, null=True, blank=True, verbose_name=_("العنوان"))
    governorate = models.CharField(db_column='Governorate', max_length=50, null=True, blank=True, verbose_name=_("المحافظة"))
    
    # Personal information
    emp_marital_status = models.CharField(db_column='Emp_Marital_Status', max_length=50, choices=MARITAL_STATUS_CHOICES, null=True, blank=True, verbose_name=_("الحالة الاجتماعية"))
    emp_nationality = models.CharField(db_column='Emp_Nationality', max_length=50, null=True, blank=True, verbose_name=_("الجنسية"))
    people_with_special_needs = models.BooleanField(db_column='People_With_Special_Needs', null=True, blank=True, verbose_name=_("ذوي الاحتياجات الخاصة"))
    national_id = models.CharField(db_column='National_ID', max_length=14, null=True, blank=True, verbose_name=_("الرقم القومي"))
    date_birth = models.DateField(db_column='Date_Birth', null=True, blank=True, verbose_name=_("تاريخ الميلاد"))
    age = models.CharField(db_column='Age', max_length=100, null=True, blank=True, verbose_name=_("العمر"))
    place_birth = models.CharField(db_column='Place_Birth', max_length=50, null=True, blank=True, verbose_name=_("محل الميلاد"))
    emp_image = models.BinaryField(db_column='Emp_Image', null=True, blank=True, editable=True, verbose_name=_("صورة الموظف"))
    personal_id_expiry_date = models.DateField(db_column='Personal_ID_Expiry_Date', null=True, blank=True, verbose_name=_("تاريخ انتهاء البطاقة الشخصية"))
    military_service_certificate = models.CharField(db_column='Military_Service_Certificate', max_length=50, null=True, blank=True, choices=MILITARY_SERVICE_CHOICES, verbose_name=_("شهادة الخدمة العسكرية"))
    
    # Employment information
    working_condition = models.CharField(db_column='Working_Condition', max_length=50, choices=WORKING_CONDITION_CHOICES, null=True, blank=True, verbose_name=_("حالة العمل"))
    # dept_code = models.IntegerField(db_column='Dept_Code', null=True, blank=True, verbose_name=_("كود القسم"))
    department = models.ForeignKey(
        Department,
        db_column='Dept_Code',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("القسم"),
        related_name='employees'  # أضف هذا السطر
    )
    dept_name = models.CharField(db_column='Dept_Name', max_length=50, null=True, blank=True, verbose_name=_("اسم القسم"))
    jop_code = models.IntegerField(db_column='Jop_Code', null=True, blank=True, verbose_name=_("كود الوظيفة"))
    jop_name = models.CharField(db_column='Jop_Name', max_length=50, null=True, blank=True, verbose_name=_("اسم الوظيفة"))
    emp_date_hiring = models.DateField(db_column='Emp_Date_Hiring', null=True, blank=True, verbose_name=_("تاريخ التعيين"))
    
    # Car details
    emp_car = models.CharField(db_column='Emp_Car', max_length=50, null=True, blank=True, verbose_name=_("السيارة"))
    car_ride_time = models.DateTimeField(db_column='Car_Ride_Time', null=True, blank=True, verbose_name=_("وقت ركوب السيارة"))
    car_pick_up_point = models.CharField(db_column='Car_Pick_Up_Point', max_length=100, null=True, blank=True, verbose_name=_("نقطة التقاط السيارة"))
    
    # Insurance details
    insurance_status = models.CharField(db_column='Insurance_Status', max_length=50, choices=INSURANCE_STATUS_CHOICES, null=True, blank=True, verbose_name=_("حالة التأمين"))
    jop_code_insurance = models.IntegerField(db_column='Jop_Code_insurance', null=True, blank=True, verbose_name=_("كود وظيفة التأمين"))
    jop_name_insurance = models.CharField(db_column='Jop_Name_insurance', max_length=50, null=True, blank=True, verbose_name=_("اسم وظيفة التأمين"))
    insurance_code = models.IntegerField(db_column='Insurance_Code', null=True, blank=True, verbose_name=_("كود التأمين")) 
    number_insurance = models.IntegerField(db_column='Number_Insurance', null=True, blank=True, verbose_name=_("رقم التأمين"))
    date_insurance_start = models.DateField(db_column='Date_Insurance_Start', null=True, blank=True, verbose_name=_("تاريخ بداية التأمين"))
    insurance_salary = models.DecimalField(db_column='Insurance_Salary', max_digits=18, decimal_places=2, null=True, blank=True, verbose_name=_("راتب التأمين"))
    percentage_insurance_payable = models.DecimalField(db_column='Percentage_Insurance_Payable', max_digits=18, decimal_places=4, null=True, blank=True, verbose_name=_("نسبة التأمين المستحق"))
    due_insurance_amount = models.DecimalField(db_column='Due_Insurance_Amount', max_digits=18, decimal_places=2, null=True, blank=True, verbose_name=_("مبلغ التأمين المستحق"))
    
    # Health card
    health_card = models.CharField(db_column='Health_Card', max_length=50, choices=health_card_choices, null=True, blank=True, verbose_name=_("بطاقة صحية"))
    health_card_number = models.IntegerField(db_column='Health_Card_Number', null=True, blank=True, verbose_name=_("رقم البطاقة الصحية"))
    health_card_start_date = models.DateField(db_column='Health_Card_Start_Date', null=True, blank=True, verbose_name=_("تاريخ بداية البطاقة الصحية"))
    health_card_renewal_date = models.DateField(db_column='Health_Card_Renewal_Date', null=True, blank=True, verbose_name=_("تاريخ تجديد البطاقة الصحية"))
    the_health_card_remains_expire = models.IntegerField(db_column='The_health_card_remains_expire', null=True, blank=True, verbose_name=_("المتبقي لانتهاء البطاقة الصحية"))
    health_card_expiration_date = models.DateField(db_column='Health_Card_Expiration_Date', null=True, blank=True, verbose_name=_("تاريخ انتهاء البطاقة الصحية"))
    hiring_date_health_card = models.DateField(db_column='Hiring_Date_Health_Card', null=True, blank=True, verbose_name=_("تاريخ تعيين البطاقة الصحية"))
    
    # Forms and documents
    form_s1 = models.BooleanField(db_column='Form_S1', null=True, blank=True, verbose_name=_("نموذج S1"))
    confirmation_insurance_entry = models.BooleanField(db_column='Confirmation_Insurance_Entry', null=True, blank=True, verbose_name=_("تأكيد دخول التأمين"))
    delivery_date_s1 = models.DateField(db_column='Delivery_Date_S1', null=True, blank=True, verbose_name=_("تاريخ تسليم S1"))
    receive_date_s1 = models.DateField(db_column='Receive_Date_S1', null=True, blank=True, verbose_name=_("تاريخ استلام S1"))
    form_s6 = models.BooleanField(db_column='Form_S6', null=True, blank=True, verbose_name=_("نموذج S6"))
    delivery_date_s6 = models.DateField(db_column='Delivery_Date_S6', null=True, blank=True, verbose_name=_("تاريخ تسليم S6"))
    receive_date_s6 = models.DateField(db_column='Receive_Date_S6', null=True, blank=True, verbose_name=_("تاريخ استلام S6"))
    entrance_date_s1 = models.DateField(db_column='Entrance_Date_S1', null=True, blank=True, verbose_name=_("تاريخ دخول S1"))
    entrance_number_s1 = models.IntegerField(db_column='Entrance_Number_S1', null=True, blank=True, verbose_name=_("رقم دخول S1"))
    entrance_date_s6 = models.DateField(db_column='Entrance_Date_S6', null=True, blank=True, verbose_name=_("تاريخ دخول S6"))
    entrance_number_s6 = models.IntegerField(db_column='Entrance_Number_S6', null=True, blank=True, verbose_name=_("رقم دخول S6"))
    
    # Skills and certifications
    skill_level_measurement_certificate = models.BooleanField(db_column='Skill_level_measurement_certificate', null=True, blank=True, verbose_name=_("شهادة قياس مستوى المهارة"))
    qualification_certificate = models.CharField(db_column='Qualification_Certificate', max_length=50, null=True, blank=True, verbose_name=_("شهادة المؤهل"))
    
    # Shift and contract
    currentweekshift = models.CharField(db_column='CurrentWeekShift', max_length=50, null=True, blank=True, verbose_name=_("وردية الأسبوع الحالي"))
    nextweekshift = models.CharField(db_column='NextWeekShift', max_length=50, null=True, blank=True, verbose_name=_("وردية الأسبوع القادم"))
    friday_operation = models.CharField(db_column='Friday_Operation', max_length=50, null=True, blank=True, verbose_name=_("عملية يوم الجمعة"))
    shift_type = models.CharField(db_column='Shift_Type', max_length=50, choices=SHIFT_TYPE_CHOICES, null=True, blank=True, verbose_name=_("نوع الوردية"))
    shift_paper = models.CharField(db_column='Shift_paper', max_length=50, null=True, blank=True, verbose_name=_("ورقة الشيفت"))
    
    # Contract details
    remaining_contract_renewal = models.IntegerField(db_column='Remaining_Contract_Renewal', null=True, blank=True, verbose_name=_("تجديد العقد المتبقي"))
    medical_exam_form_submission = models.BooleanField(db_column='Medical_Exam_Form_Submission', null=True, blank=True, verbose_name=_("تقديم استمارة الفحص الطبي"))
    contract_renewal_date = models.DateField(db_column='Contract_Renewal_Date', null=True, blank=True, verbose_name=_("تاريخ تجديد العقد"))
    contract_renewal_month = models.IntegerField(db_column='Contract_Renewal_Month', null=True, blank=True, verbose_name=_("شهر تجديد العقد"))
    contract_expiry_date = models.DateField(db_column='Contract_Expiry_Date', null=True, blank=True, verbose_name=_("تاريخ انتهاء العقد"))
    end_date_probationary_period = models.DateField(db_column='End_date_probationary_period', null=True, blank=True, verbose_name=_("تاريخ انتهاء فترة الاختبار"))
    years_since_contract_start = models.CharField(db_column='Years_Since_Contract_Start', max_length=100, null=True, blank=True, verbose_name=_("السنوات منذ بداية العقد"))
    
    # Document checklist
    birth_certificate = models.BooleanField(db_column='Birth_Certificate', null=True, blank=True, verbose_name=_("شهادة الميلاد"))
    insurance_printout = models.BooleanField(db_column='Insurance_Printout', null=True, blank=True, verbose_name=_("مطبوعة التأمين"))
    id_card_photo = models.BooleanField(db_column='ID_Card_Photo', null=True, blank=True, verbose_name=_("صورة البطاقة الشخصية"))
    personal_photos = models.BooleanField(db_column='Personal_Photos', null=True, blank=True, verbose_name=_("صور شخصية"))
    employment_contract = models.BooleanField(db_column='Employment_Contract', null=True, blank=True, verbose_name=_("عقد العمل"))
    medical_exam_form = models.BooleanField(db_column='Medical_Exam_Form', null=True, blank=True, verbose_name=_("استمارة الفحص الطبي"))
    criminal_record_check = models.BooleanField(db_column='Criminal_Record_Check', null=True, blank=True, verbose_name=_("فحص السجل الجنائي"))
    social_status_report = models.BooleanField(db_column='Social_Status_Report', null=True, blank=True, verbose_name=_("تقرير الحالة الاجتماعية"))
    
    # Work heel details
    work_heel = models.BooleanField(db_column='Work_Heel', null=True, blank=True, verbose_name=_("كعب العمل"))
    heel_work_number = models.IntegerField(db_column='Heel_Work_Number', null=True, blank=True, verbose_name=_("رقم كعب العمل"))
    heel_work_registration_date = models.DateField(db_column='Heel_Work_Registration_Date', null=True, blank=True, verbose_name=_("تاريخ تسجيل كعب العمل"))
    heel_work_recipient = models.CharField(db_column='Heel_Work_Recipient', max_length=50, null=True, blank=True, verbose_name=_("مستلم كعب العمل"))
    heel_work_recipient_address = models.CharField(db_column='Heel_Work_Recipient_Address', max_length=50, null=True, blank=True, verbose_name=_("عنوان مستلم كعب العمل"))
    
    # Resignation details
    date_resignation = models.DateField(db_column='Date_Resignation', null=True, blank=True, verbose_name=_("تاريخ الاستقالة"))
    reason_resignation = models.CharField(db_column='Reason_Resignation', max_length=100, null=True, blank=True, verbose_name=_("سبب الاستقالة"))
    confirm_exit_insurance = models.BooleanField(db_column='Confirm_Exit_Insurance', null=True, blank=True, verbose_name=_("تأكيد خروج التأمين"))
    
    def __str__(self):
        return f"{self.emp_full_name or self.emp_first_name or 'موظف'} ({self.emp_id})"
    
    class Meta:
        verbose_name = _("الموظف")
        verbose_name_plural = _("الموظفون")
        db_table = 'Tbl_Employee'  # Use the same table as the previous model
        managed = True  # Allow Django to manage this table
