from django.urls import path
from . import views

app_name = 'banks'

urlpatterns = [
    # قائمة البنوك
    path('', views.bank_list, name='list'),
    path('list/', views.bank_list, name='bank_list'),
    
    # إضافة بنك جديد
    path('add/', views.add_bank, name='add'),
    path('create/', views.add_bank, name='create'),
    
    # تفاصيل البنك
    path('<int:bank_id>/', views.bank_detail, name='detail'),
    path('detail/<int:bank_id>/', views.bank_detail, name='bank_detail'),
    
    # تعديل بنك
    path('<int:bank_id>/edit/', views.edit_bank, name='edit'),
    path('edit/<int:bank_id>/', views.edit_bank, name='edit_bank'),
    
    # حذف بنك
    path('<int:bank_id>/delete/', views.delete_bank, name='delete'),
    path('delete/<int:bank_id>/', views.delete_bank, name='delete_bank'),
    
    # إدارة فروع البنك
    path('<int:bank_id>/branches/', views.bank_branches, name='branches'),
    path('branches/<int:bank_id>/', views.bank_branches, name='bank_branches'),
    
    # API endpoints
    path('api/banks/', views.banks_api, name='api_banks'),
    path('api/bank/<int:bank_id>/', views.bank_api, name='api_bank'),
]