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
        
class SalesReportPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, orders,date_range,start_date,end_date):
        next_n=self.page.next_page_number() if self.page.has_next() else None
        prev_n=self.page.previous_page_number() if self.page.has_previous() else None
        total_orders=self.page.paginator.count
        total_sales = sum(order.total for order in orders)
        if total_orders<=0:
            return None
        return Response({
            'orders':orders,
            'date_range':date_range,
            'start_date':start_date,
            'end_date':end_date,
            'next_n':next_n,
            'prev_n':prev_n,
            'total_orders':total_orders,
            'total_sales':total_sales,
        })
        

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
        

    

