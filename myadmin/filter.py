from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from store.serializers import CategoryAdminSerializer,ProductAdminSerializer,BrandDetailsSerializer,OrderSerializer


class CategoryPagination(PageNumberPagination):
    page_size=20
    
    def get_paginated_response(self, data):
        serializer=CategoryAdminSerializer()
        total_products=self.page.paginator.count
        total_pages=total_products//self.page_size
        if total_products % self.page_size != 0:
            total_pages += 1
        # print(data)
        return Response({
            'serializer':serializer,
            'page_number':self.page.number,
            'total_pages':total_pages,
            'page_size':self.page_size,
            'count': total_products,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
        
        
class ProductPagination(PageNumberPagination):
    page_size=10
    
    def get_paginated_response(self, data):
        serializer=ProductAdminSerializer()
        total_products=self.page.paginator.count
        total_pages=total_products//self.page_size
        if total_products % self.page_size != 0:
            total_pages += 1
        # print(data)
        return Response({
            'serializer':serializer,
            'page_number':self.page.number,
            'total_pages':total_pages,
            'page_size':self.page_size,
            'count': total_products,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
        
class BrandPagination(PageNumberPagination):
    page_size=8
    
    def get_paginated_response(self, data):
        serializer=BrandDetailsSerializer()
        total_products=self.page.paginator.count
        total_pages=total_products//self.page_size
        if total_products % self.page_size != 0:
            total_pages += 1
        # print(data)
        return {
            'serializer':serializer,
            'page_number':self.page.number,
            'total_pages':total_pages,
            'page_size':self.page_size,
            'count': total_products,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        }
        

# class OrderPagination(PageNumberPagination):
#     page_size=8
    
#     def get_paginated_response(self, data):
#         serializer=OrderSerializer()
#         total_products=self.page.paginator.count
#         total_pages=total_products//self.page_size
#         if total_products % self.page_size != 0:
#             total_pages += 1
#         # print(data)
#         return {
#             # 'serializer':serializer,
#             'page_number':self.page.number,
#             'total_pages':total_pages,
#             'page_size':self.page_size,
#             'count': total_products,
#             'next': self.get_next_link(),
#             'previous': self.get_previous_link(),
#             'results': data,
#         }
        

    

