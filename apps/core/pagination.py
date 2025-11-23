"""
Custom pagination classes for the API.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class with customizable page size.
    """
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Return a paginated style Response object.
        """
        return Response({
            'status': 'success',
            'data': data,
            'pagination': {
                'page': self.page.number,
                'limit': self.page_size,
                'total': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_prev': self.page.has_previous(),
            }
        })

