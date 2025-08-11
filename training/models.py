from django.db import models
from employees.models import Employee


class TrainingProvider(models.Model):
    provider_id = models.AutoField(primary_key=True, db_column='ProviderID')
    provider_name = models.CharField(max_length=150, db_column='ProviderName')
    contact_person = models.CharField(max_length=100, db_column='ContactPerson', blank=True, null=True)
    phone = models.CharField(max_length=50, db_column='Phone', blank=True, null=True)
    email = models.EmailField(max_length=100, db_column='Email', blank=True, null=True)

    class Meta:
        db_table = 'TrainingProviders'
        verbose_name = 'مزود تدريب'
        verbose_name_plural = 'مزودو التدريب'


class TrainingCourse(models.Model):
    course_id = models.AutoField(primary_key=True, db_column='CourseID')
    course_name = models.CharField(max_length=200, db_column='CourseName')
    provider = models.ForeignKey(TrainingProvider, on_delete=models.PROTECT, db_column='ProviderID', blank=True, null=True)
    duration_hours = models.IntegerField(db_column='DurationHours', blank=True, null=True)
    cost = models.DecimalField(max_digits=18, decimal_places=2, db_column='Cost', blank=True, null=True)
    start_date = models.DateField(db_column='StartDate', blank=True, null=True)
    end_date = models.DateField(db_column='EndDate', blank=True, null=True)
    location = models.CharField(max_length=255, db_column='Location', blank=True, null=True)

    class Meta:
        db_table = 'TrainingCourses'
        verbose_name = 'دورة تدريبية'
        verbose_name_plural = 'الدورات التدريبية'


class EmployeeTraining(models.Model):
    emp_training_id = models.AutoField(primary_key=True, db_column='EmpTrainingID')
    emp = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmpID')
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, db_column='CourseID')
    enrollment_date = models.DateField(db_column='EnrollmentDate', blank=True, null=True)
    status = models.CharField(max_length=30, db_column='Status', default='Registered')
    grade = models.CharField(max_length=10, db_column='Grade', blank=True, null=True)
    certificate_path = models.CharField(max_length=500, db_column='CertificatePath', blank=True, null=True)
    notes = models.CharField(max_length=500, db_column='Notes', blank=True, null=True)

    class Meta:
        db_table = 'EmployeeTraining'
        verbose_name = 'تدريب موظف'
        verbose_name_plural = 'تدريبات الموظفين'

# Create your models here.
