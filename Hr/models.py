# هذا ملف نموذج Django تم إنشاؤه تلقائيًا.
# ستحتاج إلى القيام بما يلي يدويًا لتنظيفه:
#   * إعادة ترتيب النماذج
#   * التأكد من أن كل نموذج يحتوي على حقل واحد مع primary_key=True
#   * التأكد من أن كل ForeignKey و OneToOneField لديه `on_delete` محدد بالسلوك المطلوب
#   * إزالة أسطر `managed = True` إذا كنت ترغب في السماح لـ Django بإنشاء وتعديل وحذف الجدول
# يمكنك إعادة تسمية النماذج، ولكن لا تقم بإعادة تسمية قيم db_table أو أسماء الحقول.
from django.db import models
from django.utils import timezone


class TblEmployee(models.Model):
    emp_id = models.IntegerField(db_column='Emp_ID', primary_key=True)  # Field name made lowercase.
    emp_first_name = models.CharField(db_column='Emp_First_Name', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    emp_second_name = models.CharField(db_column='Emp_Second_Name', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    emp_full_name = models.CharField(db_column='Emp_Full_Name', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    emp_name_english = models.CharField(db_column='Emp_Name_English', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    emp_phone1 = models.CharField(db_column='Emp_Phone1', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    emp_phone2 = models.CharField(db_column='Emp_Phone2', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    emp_address = models.CharField(db_column='Emp_Address', max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    emp_marital_status = models.CharField(db_column='Emp_Marital_Status', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    emp_nationality = models.CharField(db_column='Emp_Nationality', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    people_with_special_needs = models.BooleanField(db_column='People_With_Special_Needs', blank=True, null=True)  # Field name made lowercase.
    national_id = models.CharField(db_column='National_ID', max_length=14, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    date_birth = models.DateField(db_column='Date_Birth', blank=True, null=True)  # Field name made lowercase.
    place_birth = models.CharField(db_column='Place_Birth', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    emp_image = models.BinaryField(db_column='Emp_Image', blank=True, null=True, editable=True)  # Field name made lowercase.
    # emp_image = models.ImageField(upload_to='images/', blank=True, null=True)
    emp_type = models.CharField(db_column='Emp_Type', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    working_condition = models.CharField(db_column='Working_Condition', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    dept_code = models.IntegerField(db_column='Dept_Code', blank=True, null=True)  # Field name made lowercase.
    dept_name = models.CharField(db_column='Dept_Name', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    jop_code = models.IntegerField(db_column='Jop_Code', blank=True, null=True)  # Field name made lowercase.
    jop_name = models.CharField(db_column='Jop_Name', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    emp_date_hiring = models.DateField(db_column='Emp_Date_Hiring', blank=True, null=True)  # Field name made lowercase.
    emp_car = models.CharField(db_column='Emp_Car', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    car_ride_time = models.DateTimeField(db_column='Car_Ride_Time', blank=True, null=True)  # Field name made lowercase.
    car_pick_up_point = models.CharField(db_column='Car_Pick_Up_Point', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    insurance_status = models.CharField(db_column='Insurance_Status', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    jop_code_insurance = models.IntegerField(db_column='Jop_Code_insurance', blank=True, null=True)  # Field name made lowercase.
    jop_name_insurance = models.CharField(db_column='Jop_Name_insurance', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    health_card = models.CharField(db_column='Health_Card', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    health_card_number = models.IntegerField(db_column='Health_Card_Number', blank=True, null=True)  # Field name made lowercase.
    health_card_start_date = models.DateField(db_column='Health_Card_Start_Date', blank=True, null=True)  # Field name made lowercase.
    health_card_renewal_date = models.DateField(db_column='Health_Card_Renewal_Date', blank=True, null=True)  # Field name made lowercase.
    the_health_card_remains_expire = models.IntegerField(db_column='The_health_card_remains_expire', blank=True, null=True)  # Field name made lowercase.
    health_card_expiration_date = models.DateField(db_column='Health_Card_Expiration_Date', blank=True, null=True)  # Field name made lowercase.
    number_insurance = models.IntegerField(db_column='Number_Insurance', blank=True, null=True)  # Field name made lowercase.
    date_insurance_start = models.DateField(db_column='Date_Insurance_Start', blank=True, null=True)  # Field name made lowercase.
    insurance_salary = models.DecimalField(db_column='Insurance_Salary', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    percentage_insurance_payable = models.DecimalField(db_column='Percentage_Insurance_Payable', max_digits=18, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    due_insurance_amount = models.DecimalField(db_column='Due_Insurance_Amount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    form_s1 = models.BooleanField(db_column='Form_S1', blank=True, null=True)  # Field name made lowercase.
    confirmation_insurance_entry = models.BooleanField(db_column='Confirmation_Insurance_Entry', blank=True, null=True)  # Field name made lowercase.
    delivery_date_s1 = models.DateField(db_column='Delivery_Date_S1', blank=True, null=True)  # Field name made lowercase.
    receive_date_s1 = models.DateField(db_column='Receive_Date_S1', blank=True, null=True)  # Field name made lowercase.
    form_s6 = models.BooleanField(db_column='Form_S6', blank=True, null=True)  # Field name made lowercase.
    delivery_date_s6 = models.DateField(db_column='Delivery_Date_S6', blank=True, null=True)  # Field name made lowercase.
    receive_date_s6 = models.DateField(db_column='Receive_Date_S6', blank=True, null=True)  # Field name made lowercase.
    hiring_date_health_card = models.DateField(db_column='Hiring_Date_Health_Card', blank=True, null=True)  # Field name made lowercase.
    skill_level_measurement_certificate = models.BooleanField(db_column='Skill_level_measurement_certificate', blank=True, null=True)  # Field name made lowercase.
    end_date_probationary_period = models.DateField(db_column='End_date_probationary_period', blank=True, null=True)  # Field name made lowercase.
    currentweekshift = models.CharField(db_column='CurrentWeekShift', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    nextweekshift = models.CharField(db_column='NextWeekShift', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    friday_operation = models.CharField(db_column='Friday_Operation', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    shift_type = models.CharField(db_column='Shift_Type', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    entrance_date_s1 = models.DateField(db_column='Entrance_Date_S1', blank=True, null=True)  # Field name made lowercase.
    entrance_number_s1 = models.IntegerField(db_column='Entrance_Number_S1', blank=True, null=True)  # Field name made lowercase.
    remaining_contract_renewal = models.IntegerField(db_column='Remaining_Contract_Renewal', blank=True, null=True)  # Field name made lowercase.
    medical_exam_form_submission = models.BooleanField(db_column='Medical_Exam_Form_Submission', blank=True, null=True)  # Field name made lowercase.
    years_since_contract_start = models.CharField(db_column='Years_Since_Contract_Start', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    contract_renewal_date = models.DateField(db_column='Contract_Renewal_Date', blank=True, null=True)  # Field name made lowercase.
    contract_expiry_date = models.DateField(db_column='Contract_Expiry_Date', blank=True, null=True)  # Field name made lowercase.
    insurance_code = models.IntegerField(db_column='Insurance_Code', blank=True, null=True)  # Field name made lowercase.
    personal_id_expiry_date = models.DateField(db_column='Personal_ID_Expiry_Date', blank=True, null=True)  # Field name made lowercase.
    contract_renewal_month = models.IntegerField(db_column='Contract_Renewal_Month', blank=True, null=True)  # Field name made lowercase.
    military_service_certificate = models.CharField(db_column='Military_Service_Certificate', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    qualification_certificate = models.CharField(db_column='Qualification_Certificate', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    birth_certificate = models.BooleanField(db_column='Birth_Certificate', blank=True, null=True)  # Field name made lowercase.
    insurance_printout = models.BooleanField(db_column='Insurance_Printout', blank=True, null=True)  # Field name made lowercase.
    id_card_photo = models.BooleanField(db_column='ID_Card_Photo', blank=True, null=True)  # Field name made lowercase.
    personal_photos = models.BooleanField(db_column='Personal_Photos', blank=True, null=True)  # Field name made lowercase.
    employment_contract = models.BooleanField(db_column='Employment_Contract', blank=True, null=True)  # Field name made lowercase.
    medical_exam_form = models.BooleanField(db_column='Medical_Exam_Form', blank=True, null=True)  # Field name made lowercase.
    criminal_record_check = models.BooleanField(db_column='Criminal_Record_Check', blank=True, null=True)  # Field name made lowercase.
    social_status_report = models.BooleanField(db_column='Social_Status_Report', blank=True, null=True)  # Field name made lowercase.
    work_heel = models.BooleanField(db_column='Work_Heel', blank=True, null=True)  # Field name made lowercase.
    heel_work_number = models.IntegerField(db_column='Heel_Work_Number', blank=True, null=True)  # Field name made lowercase.
    heel_work_registration_date = models.DateField(db_column='Heel_Work_Registration_Date', blank=True, null=True)  # Field name made lowercase.
    heel_work_recipient = models.CharField(db_column='Heel_Work_Recipient', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    heel_work_recipient_address = models.CharField(db_column='Heel_Work_Recipient_Address', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    entrance_number_s6 = models.IntegerField(db_column='Entrance_Number_S6', blank=True, null=True)  # Field name made lowercase.
    entrance_date_s6 = models.DateField(db_column='Entrance_Date_S6', blank=True, null=True)  # Field name made lowercase.
    shift_paper = models.CharField(db_column='Shift_paper', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    age = models.CharField(db_column='Age', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    date_resignation = models.DateField(db_column='Date_Resignation', blank=True, null=True)  # Field name made lowercase.
    reason_resignation = models.CharField(db_column='Reason_Resignation', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    mother_name = models.CharField(db_column='Mother_Name', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    confirm_exit_insurance = models.BooleanField(db_column='Confirm_Exit_Insurance', blank=True, null=True)  # Field name made lowercase.
    governorate = models.CharField(db_column='Governorate', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    manager_id = models.IntegerField(db_column='Manager_ID', blank=True, null=True)  # Field name made lowercase.
    company_id = models.IntegerField(db_column='Company_ID', blank=True, null=True)  # Field name made lowercase.
    branch_id = models.IntegerField(db_column='Branch_ID', blank=True, null=True)  # Field name made lowercase.
    work_location = models.CharField(db_column='Work_Location', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    machine_name = models.CharField(db_column='Machine_Name', max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_Employee'


class TblAttendance(models.Model):
    attendance_id = models.AutoField(db_column='Attendance_ID', primary_key=True)  # Field name made lowercase.
    emp = models.ForeignKey(TblEmployee, models.DO_NOTHING, db_column='Emp_ID')  # Field name made lowercase.
    date = models.DateField(db_column='Date')  # Field name made lowercase.
    check_in = models.DateTimeField(db_column='Check_In', blank=True, null=True)  # Field name made lowercase.
    check_out = models.DateTimeField(db_column='Check_Out', blank=True, null=True)  # Field name made lowercase.
    late_minutes = models.IntegerField(db_column='Late_Minutes', blank=True, null=True)  # Field name made lowercase.
    overtime_minutes = models.IntegerField(db_column='Overtime_Minutes', blank=True, null=True)  # Field name made lowercase.
    machine = models.ForeignKey('TblAttendancemachine', models.DO_NOTHING, db_column='Machine_ID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_Attendance'


class TblAttendancemachine(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, db_collation='Arabic_CI_AS')
    ip_address = models.CharField(max_length=15, db_collation='Arabic_CI_AS')
    port = models.IntegerField()
    machine_type = models.CharField(max_length=10, db_collation='Arabic_CI_AS')
    location = models.CharField(max_length=100, db_collation='Arabic_CI_AS', blank=True, null=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'Tbl_AttendanceMachine'


class TblAttendancerule(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, db_collation='Arabic_CI_AS')
    description = models.TextField(db_collation='Arabic_CI_AS', blank=True, null=True)
    work_schedule = models.TextField(db_collation='Arabic_CI_AS')
    late_grace_minutes = models.IntegerField()
    early_leave_grace_minutes = models.IntegerField()
    weekly_off_days = models.TextField(db_collation='Arabic_CI_AS')
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'Tbl_AttendanceRule'


class TblAttendancerules(models.Model):
    rule_id = models.AutoField(db_column='Rule_ID', primary_key=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=100, db_collation='Arabic_CI_AS')  # Field name made lowercase.
    scheduled_start = models.TimeField(db_column='Scheduled_Start')  # Field name made lowercase.
    scheduled_end = models.TimeField(db_column='Scheduled_End')  # Field name made lowercase.
    grace_period_minutes = models.IntegerField(db_column='Grace_Period_Minutes')  # Field name made lowercase.
    late_penalty_per_minute = models.DecimalField(db_column='Late_Penalty_Per_Minute', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    absent_penalty = models.DecimalField(db_column='Absent_Penalty', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_AttendanceRules'


class TblBranch(models.Model):
    branch_id = models.AutoField(db_column='Branch_ID', primary_key=True)  # Field name made lowercase.
    branch_name = models.CharField(db_column='Branch_Name', max_length=100, db_collation='Arabic_CI_AS')  # Field name made lowercase.
    company = models.ForeignKey('TblCompany', models.DO_NOTHING, db_column='Company_ID')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_Branch'


class TblCar(models.Model):
    car_id = models.IntegerField(db_column='Car_ID', primary_key=True)  # Field name made lowercase.
    car_name = models.CharField(db_column='Car_Name', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    car_type = models.CharField(db_column='Car_Type', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    car_salary = models.DecimalField(db_column='Car_Salary', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    car_salary_farda = models.DecimalField(db_column='Car_Salary_Farda', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    supplier = models.CharField(db_column='Supplier', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    contract_type = models.CharField(db_column='Contract_Type', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    car_number = models.CharField(db_column='Car_Number', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    car_license_expiration_date = models.DateTimeField(db_column='Car_License_Expiration_Date', blank=True, null=True)  # Field name made lowercase.
    driver_name = models.CharField(db_column='Driver_Name', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    driver_phone = models.CharField(db_column='Driver_Phone', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    driver_license_expiration_date = models.DateTimeField(db_column='Driver_License_Expiration_Date', blank=True, null=True)  # Field name made lowercase.
    is_active = models.BooleanField(db_column='Is_Active')  # Field name made lowercase.
    shift_type = models.CharField(db_column='Shift_Type', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    contract_type_farada = models.CharField(db_column='Contract_Type_Farada', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_Car'


class TblCarAttendance(models.Model):
    attendance_id = models.AutoField(db_column='Attendance_ID', primary_key=True)  # Field name made lowercase.
    car = models.ForeignKey(TblCar, models.DO_NOTHING, db_column='Car_ID')  # Field name made lowercase.
    attendance_date = models.DateTimeField(db_column='Attendance_Date')  # Field name made lowercase.
    attendance_code = models.IntegerField(db_column='Attendance_Code', blank=True, null=True)  # Field name made lowercase.
    check_in = models.TimeField(db_column='Check_In', blank=True, null=True)  # Field name made lowercase.
    check_out = models.TimeField(db_column='Check_Out', blank=True, null=True)  # Field name made lowercase.
    shift_type = models.CharField(db_column='Shift_Type', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    salary = models.DecimalField(db_column='Salary', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    delay_type = models.CharField(db_column='Delay_Type', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    deduction = models.DecimalField(db_column='Deduction', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    manual_deduction = models.DecimalField(db_column='Manual_Deduction', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    notes = models.CharField(db_column='Notes', max_length=500, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    attendance_month = models.IntegerField(db_column='Attendance_Month', blank=True, null=True)  # Field name made lowercase.
    attendance_year = models.IntegerField(db_column='Attendance_Year', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_Car_Attendance'


class TblCompany(models.Model):
    company_id = models.AutoField(db_column='Company_ID', primary_key=True)  # Field name made lowercase.
    company_name = models.CharField(db_column='Company_Name', max_length=100, db_collation='Arabic_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_Company'


class TblDepartment(models.Model):
    dept_code = models.IntegerField(db_column='Dept_Code', blank=True, null=True)  # Field name made lowercase.
    dept_name = models.CharField(db_column='Dept_Name', max_length=250, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_Department'


class TblEmployeeanalytics(models.Model):
    analytics_id = models.AutoField(db_column='Analytics_ID', primary_key=True)  # Field name made lowercase.
    emp = models.ForeignKey(TblEmployee, models.DO_NOTHING, db_column='Emp_ID')  # Field name made lowercase.
    year = models.IntegerField(db_column='Year')  # Field name made lowercase.
    month = models.IntegerField(db_column='Month')  # Field name made lowercase.
    total_working_days = models.IntegerField(db_column='Total_Working_Days')  # Field name made lowercase.
    days_present = models.IntegerField(db_column='Days_Present', blank=True, null=True)  # Field name made lowercase.
    days_absent = models.IntegerField(db_column='Days_Absent', blank=True, null=True)  # Field name made lowercase.
    late_minutes = models.IntegerField(db_column='Late_Minutes', blank=True, null=True)  # Field name made lowercase.
    gross_salary = models.DecimalField(db_column='Gross_Salary', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    net_salary = models.DecimalField(db_column='Net_Salary', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    average_evaluation_score = models.DecimalField(db_column='Average_Evaluation_Score', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    leaves_taken = models.IntegerField(db_column='Leaves_Taken', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_EmployeeAnalytics'


class TblEmployeeattendancerule(models.Model):
    id = models.BigAutoField(primary_key=True)
    effective_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    attendance_rule = models.ForeignKey(TblAttendancerule, models.DO_NOTHING)
    employee = models.ForeignKey(TblEmployee, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'Tbl_EmployeeAttendanceRule'


class TblEmployeesalaryitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    employee = models.ForeignKey(TblEmployee, models.DO_NOTHING)
    salary_item = models.ForeignKey('TblSalaryitem', models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'Tbl_EmployeeSalaryItem'


class TblEvaluation(models.Model):
    eval_id = models.AutoField(db_column='Eval_ID', primary_key=True)  # Field name made lowercase.
    emp = models.ForeignKey(TblEmployee, models.DO_NOTHING, db_column='Emp_ID')  # Field name made lowercase.
    eval_date = models.DateTimeField(db_column='Eval_Date')  # Field name made lowercase.
    evaluator_id = models.IntegerField(db_column='Evaluator_ID', blank=True, null=True)  # Field name made lowercase.
    score = models.DecimalField(db_column='Score', max_digits=5, decimal_places=2)  # Field name made lowercase.
    comments = models.TextField(db_column='Comments', db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    evaluation_type = models.CharField(db_column='Evaluation_Type', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_Evaluation'


class TblEvaluationcriteria(models.Model):
    criteria_id = models.AutoField(db_column='Criteria_ID', primary_key=True)  # Field name made lowercase.
    criteria_name = models.CharField(db_column='Criteria_Name', max_length=100, db_collation='Arabic_CI_AS')  # Field name made lowercase.
    description = models.TextField(db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_EvaluationCriteria'


class TblEvaluationscores(models.Model):
    evalscore_id = models.AutoField(db_column='EvalScore_ID', primary_key=True)  # Field name made lowercase.
    eval = models.ForeignKey(TblEvaluation, models.DO_NOTHING, db_column='Eval_ID')  # Field name made lowercase.
    criteria = models.ForeignKey(TblEvaluationcriteria, models.DO_NOTHING, db_column='Criteria_ID')  # Field name made lowercase.
    score = models.DecimalField(db_column='Score', max_digits=5, decimal_places=2)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_EvaluationScores'


class TblHrtask(models.Model):
    task_id = models.AutoField(db_column='Task_ID', primary_key=True)  # Field name made lowercase.
    task_name = models.CharField(db_column='Task_Name', max_length=100, db_collation='Arabic_CI_AS')  # Field name made lowercase.
    task_description = models.TextField(db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    start_date = models.DateField(db_column='Start_Date')  # Field name made lowercase.
    end_date = models.DateField(db_column='End_Date')  # Field name made lowercase.
    department = models.CharField(db_column='Department', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    assigned_to = models.ForeignKey(TblEmployee, models.DO_NOTHING, db_column='Assigned_To', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    reminder_days = models.IntegerField(db_column='Reminder_Days', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_HRTask'


class TblJop(models.Model):
    jop_code = models.IntegerField(db_column='Jop_Code', primary_key=True)  # Field name made lowercase.
    jop_name = models.CharField(db_column='Jop_Name', max_length=50, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.
    dept_code = models.IntegerField(db_column='Dept_Code', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_Jop'


class TblJopNameInsurance(models.Model):
    jop_code_insurance = models.IntegerField(db_column='Jop_Code_insurance', primary_key=True)  # Field name made lowercase.
    jop_name_insurance = models.CharField(db_column='Jop_Name_insurance', max_length=200, db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_Jop_Name_insurance'


class TblLeave(models.Model):
    leave_id = models.AutoField(db_column='Leave_ID', primary_key=True)  # Field name made lowercase.
    emp = models.ForeignKey(TblEmployee, models.DO_NOTHING, db_column='Emp_ID')  # Field name made lowercase.
    leave_type = models.ForeignKey('TblLeavetype', models.DO_NOTHING, db_column='Leave_Type_ID')  # Field name made lowercase.
    start_date = models.DateField(db_column='Start_Date')  # Field name made lowercase.
    end_date = models.DateField(db_column='End_Date')  # Field name made lowercase.
    total_days = models.IntegerField(db_column='Total_Days', blank=True, null=True)  # Field name made lowercase.
    leave_status = models.CharField(db_column='Leave_Status', max_length=50, db_collation='Arabic_CI_AS')  # Field name made lowercase.
    request_date = models.DateTimeField(db_column='Request_Date')  # Field name made lowercase.
    approval_date = models.DateTimeField(db_column='Approval_Date', blank=True, null=True)  # Field name made lowercase.
    comments = models.TextField(db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_Leave'


class TblLeavetype(models.Model):
    leave_type_id = models.AutoField(db_column='Leave_Type_ID', primary_key=True)  # Field name made lowercase.
    leave_type_name = models.CharField(db_column='Leave_Type_Name', max_length=50, db_collation='Arabic_CI_AS')  # Field name made lowercase.
    description = models.TextField(db_collation='Arabic_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_LeaveType'


class TblOfficialholiday(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, db_collation='Arabic_CI_AS')
    date = models.DateField()
    description = models.TextField(db_collation='Arabic_CI_AS', blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'Tbl_OfficialHoliday'
        unique_together = (('name', 'date'),)


class TblPayroll(models.Model):
    payrollid = models.AutoField(db_column='PayrollID', primary_key=True)  # Field name made lowercase.
    emp = models.ForeignKey(TblEmployee, models.DO_NOTHING, db_column='Emp_ID')  # Field name made lowercase.
    payrollperiod = models.DateField(db_column='PayrollPeriod')  # Field name made lowercase.
    basesalary = models.DecimalField(db_column='BaseSalary', max_digits=18, decimal_places=2)  # Field name made lowercase.
    paymentdate = models.DateField(db_column='PaymentDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_Payroll'


class TblPayrolldetail(models.Model):
    payrolldetailid = models.AutoField(db_column='PayrollDetailID', primary_key=True)  # Field name made lowercase.
    payrollid = models.ForeignKey(TblPayroll, models.DO_NOTHING, db_column='PayrollID')  # Field name made lowercase.
    payrollitemid = models.ForeignKey('TblPayrollitemmaster', models.DO_NOTHING, db_column='PayrollItemID')  # Field name made lowercase.
    computedvalue = models.DecimalField(db_column='ComputedValue', max_digits=18, decimal_places=2)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_PayrollDetail'


class TblPayrollentry(models.Model):
    id = models.BigAutoField(primary_key=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    variable_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2)
    overtime = models.DecimalField(max_digits=10, decimal_places=2)
    penalties = models.DecimalField(max_digits=10, decimal_places=2)
    total_salary = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(db_collation='Arabic_CI_AS', blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    employee = models.ForeignKey(TblEmployee, models.DO_NOTHING)
    payroll_period = models.ForeignKey('TblPayrollperiod', models.DO_NOTHING, default=timezone.now)

    class Meta:
        managed = True
        db_table = 'Tbl_PayrollEntry'


class TblPayrollitemdetail(models.Model):
    id = models.BigAutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payroll_entry = models.ForeignKey(TblPayrollentry, models.DO_NOTHING)
    salary_item = models.ForeignKey('TblSalaryitem', models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'Tbl_PayrollItemDetail'


class TblPayrollitemmaster(models.Model):
    payrollitemid = models.AutoField(db_column='PayrollItemID', primary_key=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='ItemName', max_length=100, db_collation='Arabic_CI_AS')  # Field name made lowercase.
    itemtype = models.CharField(db_column='ItemType', max_length=50, db_collation='Arabic_CI_AS')  # Field name made lowercase.
    calculationmethod = models.CharField(db_column='CalculationMethod', max_length=50, db_collation='Arabic_CI_AS')  # Field name made lowercase.
    valueparameter = models.DecimalField(db_column='ValueParameter', max_digits=18, decimal_places=2)  # Field name made lowercase.
    sortorder = models.IntegerField(db_column='SortOrder', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_PayrollItemMaster'


class TblPickuppoint(models.Model):
    pickuppoint_id = models.AutoField(db_column='PickupPoint_ID', primary_key=True)  # Field name made lowercase.
    pickuppoint_name = models.CharField(db_column='PickupPoint_Name', max_length=100, db_collation='Arabic_CI_AS')  # Field name made lowercase.
    car = models.ForeignKey(TblCar, models.DO_NOTHING, db_column='Car_ID')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Tbl_PickupPoint'


class TblSalaryitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, db_collation='Arabic_CI_AS')
    item_type = models.CharField(max_length=20, db_collation='Arabic_CI_AS')
    calculation_method = models.CharField(max_length=20, db_collation='Arabic_CI_AS')
    affects_total = models.BooleanField()
    description = models.TextField(db_collation='Arabic_CI_AS', blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'Tbl_SalaryItem'


class LeaveType(models.Model):
    name = models.CharField(max_length=100, verbose_name='اسم نوع الإجازة')
    code = models.CharField(max_length=20, unique=True, verbose_name='كود نوع الإجازة')
    description = models.TextField(blank=True, null=True, verbose_name='وصف')
    max_days_per_year = models.PositiveIntegerField(default=0, verbose_name='الحد الأقصى للأيام في السنة')
    is_paid = models.BooleanField(default=True, verbose_name='مدفوعة الأجر')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        verbose_name = 'نوع الإجازة'
        verbose_name_plural = 'أنواع الإجازات'
        db_table = 'Hr_LeaveType'
        ordering = ['name']
        managed = True

    def __str__(self):
        return self.name


class Employee(models.Model):
    # This is a placeholder for the Employee model referenced in EmployeeLeave
    # The actual implementation should be based on your system's requirements
    name = models.CharField(max_length=100, verbose_name='اسم الموظف')

    class Meta:
        verbose_name = 'موظف'
        verbose_name_plural = 'الموظفين'
        db_table = 'Hr_Employee'
        managed = True

    def __str__(self):
        return self.name


class EmployeeLeave(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('approved', 'موافق عليه'),
        ('rejected', 'مرفوض'),
        ('cancelled', 'ملغى')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves', verbose_name='الموظف')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='employee_leaves', verbose_name='نوع الإجازة')
    start_date = models.DateField(verbose_name='تاريخ البداية')
    end_date = models.DateField(verbose_name='تاريخ النهاية')
    days_count = models.PositiveIntegerField(verbose_name='عدد الأيام')
    reason = models.TextField(verbose_name='السبب')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    approved_by = models.ForeignKey('accounts.Users_Login_New', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves', verbose_name='تمت الموافقة بواسطة')
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الموافقة')
    rejection_reason = models.TextField(null=True, blank=True, verbose_name='سبب الرفض')
    notes = models.TextField(null=True, blank=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        verbose_name = 'إجازة الموظف'
        verbose_name_plural = 'إجازات الموظفين'
        db_table = 'Hr_EmployeeLeave'
        ordering = ['-start_date']
        managed = True

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"


class TblPayrollperiod(models.Model):
    id = models.BigAutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(db_collation='Arabic_CI_AS', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Tbl_PayrollPeriod'
