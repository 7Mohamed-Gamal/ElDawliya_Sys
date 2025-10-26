from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('home/', views.dashboard, name='home'),

    # Loan Types
    path('types/', views.loan_type_list, name='loan_type_list'),
    path('types/add/', views.add_loan_type, name='add_loan_type'),
    path('types/<int:type_id>/', views.loan_type_detail, name='loan_type_detail'),

    # Employee Loans
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/add/', views.add_loan, name='add_loan'),
    path('loans/<int:loan_id>/', views.loan_detail, name='loan_detail'),
    path('loans/<int:loan_id>/edit/', views.edit_loan, name='edit_loan'),
    path('loans/<int:loan_id>/approve/', views.approve_loan, name='approve_loan'),
    path('loans/<int:loan_id>/reject/', views.reject_loan, name='reject_loan'),

    # Installments
    path('installments/', views.installment_list, name='installment_list'),
    path('installments/<int:installment_id>/pay/', views.pay_installment, name='pay_installment'),

    # Employee Portal
    path('my-loans/', views.my_loans, name='my_loans'),
    path('request-loan/', views.request_loan, name='request_loan'),

    # Reports & Export
    path('reports/', views.reports, name='reports'),
    path('export/', views.export_loans, name='export_loans'),

    # AJAX Endpoints
    path('ajax/calculate-installments/', views.calculate_installments, name='calculate_installments'),
    path('ajax/eligibility-check/<int:emp_id>/', views.loan_eligibility_check, name='loan_eligibility_check'),
]

