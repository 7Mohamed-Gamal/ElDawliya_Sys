"""
URLs للبحث المتقدم والذكي
"""

from django.urls import path
from ..views.search_views import (
    advanced_search_view,
    simple_search_view,
    search_api,
    search_suggestions_api,
    smart_search_api,
    save_search_api,
    saved_searches_api,
    execute_saved_search_api,
    delete_saved_search_api,
    toggle_favorite_search,
    search_analytics_view,
    search_management_view,
    rebuild_search_index,
    create_search_filter,
    create_smart_pattern,
    export_search_data,
)

app_name = 'search'

urlpatterns = [
    # صفحات البحث
    path('', advanced_search_view, name='advanced'),
    path('simple/', simple_search_view, name='simple'),
    
    # API البحث
    path('api/', search_api, name='api'),
    path('suggestions/', search_suggestions_api, name='suggestions'),
    path('smart/', smart_search_api, name='smart'),
    
    # إدارة عمليات البحث المحفوظة
    path('save/', save_search_api, name='save'),
    path('saved/', saved_searches_api, name='saved_list'),
    path('execute/<uuid:search_id>/', execute_saved_search_api, name='execute'),
    path('delete/<uuid:search_id>/', delete_saved_search_api, name='delete'),
    path('favorite/<uuid:search_id>/', toggle_favorite_search, name='toggle_favorite'),
    
    # التحليلات والإدارة
    path('analytics/', search_analytics_view, name='analytics'),
    path('management/', search_management_view, name='management'),
    path('rebuild-index/', rebuild_search_index, name='rebuild_index'),
    path('export/', export_search_data, name='export'),
    
    # إدارة الفلاتر والأنماط
    path('filters/create/', create_search_filter, name='create_filter'),
    path('patterns/create/', create_smart_pattern, name='create_pattern'),
]