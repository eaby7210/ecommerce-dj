from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from store.serializers import CategoryAdminSerializer


class CustomPagination(PageNumberPagination):
    page_size=20
    
    def get_paginated_response(self, data):
        total_products=self.page.paginator.count
        total_pages=total_products//self.page_size
        if total_products % self.page_size != 0:
            total_pages += 1
        # print(data)
        return Response({
            'page_number':self.page.number,
            'total_pages':total_pages,
            'page_size':self.page_size,
            'count': total_products,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })