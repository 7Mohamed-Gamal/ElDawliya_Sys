"""
HR API Pagination - تصفح واجهات برمجة التطبيقات للموارد البشرية
"""
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict

class CustomPageNumberPagination(PageNumberPagination):
    """تصفح مخصص بأرقام الصفحات"""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

class LargeResultsSetPagination(PageNumberPagination):
    """تصفح للنتائج الكبيرة"""
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('pagination_info', {
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'start_index': self.page.start_index(),
                'end_index': self.page.end_index()
            })
        ]))

class SmallResultsSetPagination(PageNumberPagination):
    """تصفح للنتائج الصغيرة"""
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

class CustomLimitOffsetPagination(LimitOffsetPagination):
    """تصفح مخصص بالحد والإزاحة"""
    
    default_limit = 20
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('limit', self.limit),
            ('offset', self.offset),
            ('results', data)
        ]))

class AttendanceRecordPagination(PageNumberPagination):
    """تصفح مخصص لسجلات الحضور"""
    
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('summary', {
                'total_records': self.page.paginator.count,
                'records_on_page': len(data),
                'showing_from': self.page.start_index(),
                'showing_to': self.page.end_index()
            })
        ]))

class EmployeePagination(PageNumberPagination):
    """تصفح مخصص للموظفين"""
    
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('employee_summary', {
                'total_employees': self.page.paginator.count,
                'employees_on_page': len(data),
                'page_range': list(self.page.paginator.page_range)
            })
        ]))

class ReportPagination(PageNumberPagination):
    """تصفح مخصص للتقارير"""
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('report_info', {
                'total_records': self.page.paginator.count,
                'records_per_page': self.get_page_size(self.request),
                'is_last_page': not self.page.has_next(),
                'is_first_page': not self.page.has_previous()
            })
        ]))

class NoPagination:
    """بدون تصفح - لإرجاع جميع النتائج"""
    
    def paginate_queryset(self, queryset, request, view=None):
        return None
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', len(data)),
            ('results', data)
        ]))