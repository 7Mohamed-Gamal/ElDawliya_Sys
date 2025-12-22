"""
Enhanced pagination classes for API responses
فئات التصفح المحسنة لاستجابات API
"""

from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for API responses with Arabic support
    التصفح القياسي لاستجابات API مع دعم العربية
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        """
        Return paginated response with Arabic labels
        إرجاع استجابة مصفحة مع تسميات عربية
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('meta', {
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'start_index': self.page.start_index(),
                'end_index': self.page.end_index(),
            })
        ]))


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for large datasets
    التصفح للمجموعات الكبيرة من البيانات
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class SmallResultsSetPagination(PageNumberPagination):
    """
    Pagination for small datasets or detailed views
    التصفح للمجموعات الصغيرة أو العروض المفصلة
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    Limit/Offset pagination with Arabic support
    تصفح الحد/الإزاحة مع دعم العربية
    """
    default_limit = 20
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100

    def get_paginated_response(self, data):
        """
        Return paginated response with Arabic labels
        إرجاع استجابة مصفحة مع تسميات عربية
        """
        return Response(OrderedDict([
            ('count', self.count),
            ('limit', self.limit),
            ('offset', self.offset),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('meta', {
                'has_next': self.get_next_link() is not None,
                'has_previous': self.get_previous_link() is not None,
                'total_pages': (self.count + self.limit - 1) // self.limit if self.limit else 1,
                'current_page': (self.offset // self.limit) + 1 if self.limit else 1,
            })
        ]))


class ReportPagination(PageNumberPagination):
    """
    Special pagination for reports with larger page sizes
    تصفح خاص للتقارير مع أحجام صفحات أكبر
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        """
        Return paginated response optimized for reports
        إرجاع استجابة مصفحة محسنة للتقارير
        """
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
                'records_in_page': len(data),
                'is_last_page': not self.page.has_next(),
                'is_first_page': not self.page.has_previous(),
            })
        ]))