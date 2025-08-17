from django.urls import path
from . import views

app_name = 'payrolls'

urlpatterns = [
    # لوحة التحكم الرئيسية
    path('', views.dashboard, name='dashboard'),
    
    # إدارة الرواتب
    path('salary-list/', views.salary_list, name='salary_list'),
    
    # إدارة دورات الرواتب
    path('payroll-runs/', views.payroll_runs, name='payroll_runs'),
    
    # كشوف الرواتب
    path('payslips/', views.payslips, name='payslips'),
    
    # التقارير
    path('reports/', views.reports, name='reports'),
]