from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
# from django.core.cache import cache
from django.contrib import messages
import datetime
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import TemplateHTMLRenderer
from django.db import transaction
from django.db.models import Count, Case, When, Value, CharField
from django.db.models.aggregates import Count,Sum,Avg
from django.db.models.functions import ExtractMonth,ExtractYear
from store.models import *
from store.serializers import *
from .filter import *
from core.serializers import UserUpdateSerializer
from rest_framework.response import Response
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAdminUser

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO


User=get_user_model()

# Create your views here.



class Dashboard(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAdminUser]
    MONTH_NAMES = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
        7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    
    def get_table_style(self):
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])

    def generate_pdf(self, context):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title = "E-Commerce"
        generation_date = datetime.datetime.now().strftime("%Y-%m-%d")
        title_paragraph = Paragraph(f"{title}<br/>Report - {generation_date}", styles['Title'])
        elements.append(title_paragraph)
        elements.append(Spacer(1, 0.5 * inch))

        # Membership counts table
        membership_data = [['Membership Type', 'Number of Customers']] + [[membership['membership_display'], membership['count']] for membership in context['membership_counts']]
        membership_table = Table(membership_data, hAlign='LEFT')
        membership_table.setStyle(self.get_table_style())
        elements.append(Paragraph("Number of customers per membership type", styles['Heading2']))
        elements.append(membership_table)
        elements.append(Spacer(1, 0.5 * inch))

        # Order status table
        status_data = [['Order Status', 'Number of Orders']] + [[status['order_status_display'], status['count']] for status in context['status_counts']]
        status_table = Table(status_data, hAlign='LEFT')
        status_table.setStyle(self.get_table_style())
        elements.append(Paragraph("Orders broken down by status", styles['Heading2']))
        elements.append(status_table)
        elements.append(Spacer(1, 0.5 * inch))

        # Total and average order value
        elements.append(Paragraph(f"Total Order Value: {context['total_order_value']}", styles['BodyText']))
        elements.append(Paragraph(f"Average Order Value: {context['average_order_value']}", styles['BodyText']))
        elements.append(Spacer(1, 0.5 * inch))

        # Payment method table
        payment_method_data = [['Payment Method', 'Number of Orders']] + [[payment['payment_method_display'], payment['count']] for payment in context['payment_method_counts']]
        payment_method_table = Table(payment_method_data, hAlign='LEFT')
        payment_method_table.setStyle(self.get_table_style())
        elements.append(Paragraph("Payment method distribution", styles['Heading2']))
        elements.append(payment_method_table)
        elements.append(Spacer(1, 0.5 * inch))

        # Coupon usage
        elements.append(Paragraph(f"Orders with coupons applied: {context['orders_with_coupons']}", styles['BodyText']))
        elements.append(Paragraph(f"Orders without coupons applied: {context['orders_without_coupons']}", styles['BodyText']))
        elements.append(Spacer(1, 0.5 * inch))

        # Orders per customer table
        orders_per_customer_data = [['Customer', 'Number of Orders']] + [[order['customer'], order['count']] for order in context['orders_per_customer']]
        orders_per_customer_table = Table(orders_per_customer_data, hAlign='LEFT')
        orders_per_customer_table.setStyle(self.get_table_style())
        elements.append(Paragraph("Orders per customer", styles['Heading2']))
        elements.append(orders_per_customer_table)
        elements.append(Spacer(1, 0.5 * inch))

        # Order item status table
        order_item_status_data = [['Order Item Status', 'Number of Items']] + [[status['status_display'], status['count']] for status in context['order_item_status_counts']]
        order_item_status_table = Table(order_item_status_data, hAlign='LEFT')
        order_item_status_table.setStyle(self.get_table_style())
        elements.append(Paragraph("Status distribution of order items", styles['Heading2']))
        elements.append(order_item_status_table)
        elements.append(Spacer(1, 0.5 * inch))

        # Most ordered products table
        most_ordered_products_data = [['Id', 'Product Title', 'Number of Orders']] + [[product['product__id'], product['product__title'], product['count']] for product in context['most_ordered_products']]
        most_ordered_products_table = Table(most_ordered_products_data, hAlign='LEFT')
        most_ordered_products_table.setStyle(self.get_table_style())
        elements.append(Paragraph("Most frequently ordered products", styles['Heading2']))
        elements.append(most_ordered_products_table)
        elements.append(Spacer(1, 0.5 * inch))

        # Top brands table
        top_brands_data = [['Brand', 'Number of Orders']] + [[brand['product__brand__title'], brand['total_orders']] for brand in context['top_brands']]
        top_brands_table = Table(top_brands_data, hAlign='LEFT')
        top_brands_table.setStyle(self.get_table_style())
        elements.append(Paragraph("Top 10 Brands", styles['Heading2']))
        elements.append(top_brands_table)
        elements.append(Spacer(1, 0.5 * inch))

        # Top categories table
        top_categories_data = [['Category', 'Number of Orders']] + [[category['product__category__title'], category['total_orders']] for category in context['top_categories']]
        top_categories_table = Table(top_categories_data, hAlign='LEFT')
        top_categories_table.setStyle(self.get_table_style())
        elements.append(Paragraph("Top 10 Categories", styles['Heading2']))
        elements.append(top_categories_table)
        elements.append(Spacer(1, 0.5 * inch))

        # Build PDF
        doc.build(elements)

        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')      



    def get(self, request):
        mode = request.query_params.get('mode')

        orders = Order.objects.all()
        users = User.objects.prefetch_related('customer').all()

        # Aggregate order data
        order_years = orders.annotate(year=ExtractYear("placed_at")).values("year").annotate(count=Count("id")).values("year", "count")
        order_months = orders.annotate(month=ExtractMonth("placed_at")).values("month").annotate(count=Count("id")).values("month", "count").order_by("month")
        total_order_value = orders.aggregate(Sum('total'))['total__sum']
        average_order_value = orders.aggregate(Avg('total'))['total__avg']


        if average_order_value is not None:
            average_order_value = round(average_order_value, 2)

        # Membership counts
        membership_display_case = Case(
            *[When(membership=choice[0], then=Value(choice[1])) for choice in Customer.MEMBERSHIP_CHOICES],
            output_field=CharField()
        )
        membership_counts = Customer.objects.annotate(
            membership_display=membership_display_case
        ).values('membership_display').annotate(count=Count('id'))

        # Order status counts
        order_status_display_case = Case(
            *[When(order_status=choice[0], then=Value(choice[1])) for choice in Order.ORDER_STATUS_CHOICES],
            output_field=CharField()
        )
        status_counts = orders.annotate(
            order_status_display=order_status_display_case
        ).values('order_status_display').annotate(count=Count('id'))

        # Payment method counts
        payment_method_display_case = Case(
            *[When(payment_method=choice[0], then=Value(choice[1])) for choice in Order.PAYMENT_METHOD_CHOICES],
            output_field=CharField()
        )
        payment_method_counts = orders.annotate(
            payment_method_display=payment_method_display_case
        ).values('payment_method_display').annotate(count=Count('id'))

        # Coupon usage
        orders_with_coupons = orders.filter(applied_coupon__isnull=False).count()
        orders_without_coupons = orders.filter(applied_coupon__isnull=True).count()

        # Orders per customer
        orders_per_customer = orders.values('customer').annotate(count=Count('id'))

        # Order item status counts
        order_item_status_display_case = Case(
            *[When(status=choice[0], then=Value(choice[1])) for choice in OrderItem.STATUS_CHOICES],
            output_field=CharField()
        )
        order_item_status_counts = OrderItem.objects.annotate(
            status_display=order_item_status_display_case
        ).values('status_display').annotate(count=Count('id'))

        # Most ordered products
        most_ordered_products = OrderItem.objects.values('product__id', 'product__title').annotate(count=Count('id')).order_by('-count')[:10]

        # Top brands
        top_brands = (
            OrderItem.objects
            .values('product__brand__id', 'product__brand__title')
            .annotate(total_orders=Count('id'))
            .order_by('-total_orders')[:10]
        )

        # Top categories
        top_categories = (
            OrderItem.objects
            .values('product__category__id', 'product__category__title')
            .annotate(total_orders=Count('id'))
            .order_by('-total_orders')[:10]
        )

        context = {
            'user_count': users.count(),
            'active_user_count': users.filter(is_active=True).count(),
            'order_count': orders.count(),
            'order_to_process': orders.filter(order_status__in=['PL', 'PR', 'RR']).count(),
            'years_list': [entry['year'] for entry in order_years],
            'months_list': [entry['month'] for entry in order_months],
            'y_order_count': [entry['count'] for entry in order_years],
            'm_orders_count': [entry['count'] for entry in order_months],
            'total_order_value': total_order_value,
            'average_order_value': average_order_value,
            'membership_counts': membership_counts,
            'status_counts': status_counts,
            'payment_method_counts': payment_method_counts,
            'orders_with_coupons': orders_with_coupons,
            'orders_without_coupons': orders_without_coupons,
            'orders_per_customer': orders_per_customer,
            'order_item_status_counts': order_item_status_counts,
            'most_ordered_products': most_ordered_products,
            'top_brands': top_brands,
            'top_categories': top_categories,
        }

        if mode == 'pdfgen':
            return self.generate_pdf(context)
        else:
            return Response(context, template_name='admin/dashboard.html', content_type='text/html')

class UserViewSet(ModelViewSet):
    queryset=Customer.objects.select_related('user').all()
    serializer_class=CustomerSerializer
    filter_backends=[DjangoFilterBackend]
    filterset_fields=[]
    renderer_classes=[TemplateHTMLRenderer]
    pagination_class=PageNumberPagination
    permission_classes=[IsAdminUser]
    
    def get_template_names(self) -> list[str]:
        if self.action in ['update','retrieve']:
            return ['admin/customer_edit.html']
        return ['admin/customers.html']
    
    def get_serializer_context(self):
        return super().get_serializer_context()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user_data={key.split(".")[1]: value for key, value in request.data.items()  if key.startswith("user.")}
        customer_data = {key: value for key, value in request.data.items() if not key.startswith("user.")}
        if not 'is_active' in user_data:
            user_data['is_active']=False
        if not 'is_staff' in user_data:
            user_data['is_staff']=False
  
        user_serializer=UserUpdateSerializer(instance.user,data=user_data,partial=True)
        if user_serializer.is_valid():
            serializer=CustomerUpdateSerializer(instance,data=customer_data,partial=True)
            if serializer.is_valid():
                user_serializer.save()
                serializer.save()
                customer_data['user']=user_serializer.data
                # cache.invalidate_queries(Customer.objects)
                if getattr(instance, '_prefetched_objects_cache', None):
                    instance._prefetched_objects_cache = {}
                if getattr(instance.user, '_prefetched_objects_cache', None):
                    instance.user._prefetched_objects_cache = {}
                messages.success(request,"User profile updated successfully")
                return HttpResponse("success",status=200)
            else:
         
                
                return HttpResponse(serializer.errors,status=406)
        else:
            return HttpResponse(user_serializer.errors,status=406)
        

    def create(self, request, *args, **kwargs):
 
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            messages.success(request,f"User details added successfully")
            return redirect('admin-users-list')
        else:
            errors=[f"{field} =>{error[0]}" for field,error in serializer.errors.items()]
  
            for error in errors:
                messages.error(request,error)
            return redirect('admin-users-list')
            
     
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CustomerUpdateSerializer(instance)
        context={
            'serializer':serializer,
            'user':serializer.data   
        }

        return Response(context,status=status.HTTP_200_OK)
    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.queryset, many=True)
        context={
            'users': serializer.data,
            'serializer':UserSerializer()
        }
       
        response=Response(context, status=status.HTTP_200_OK)
        response['Cache-Control'] = 'no-cache'
        return response


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_class = ProductFilter
    pagination_class = ProductPagination
    permission_classes = [IsAdminUser]
    search_fields = ['title', 'id']
    ordering_fields = ['unit_price', 'last_update']
    renderer_classes=[TemplateHTMLRenderer]
    

    def get_serializer(self, *args, **kwargs):
        serializer_class=None
        if self.action in ['list']:
            serializer_class=ProductSerializer
        else:
            serializer_class=ProductAdminSerializer
            
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)
    
    def get_template_names(self) -> list[str]:
         if self.action in ['retrieve']: 
             return ["admin/product_edit.html"]
         else:
             return ["admin/products_add.html"]
   
    def get_serializer_context(self):
        return {'request':self.request}
    
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        context={
            'serializer':serializer,
            'product':serializer.data
            
        }
        return Response(context,status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
 
        serializer=ProductAdminSerializer(instance,data=request.data,partial=True)
        if serializer.is_valid():
            
            if not 'active' in serializer.validated_data:
                serializer.validated_data['active']=False
            serializer.save()
            
            messages.success(request,"Product updated successfully")
            return HttpResponse("success",status=200)
        else:
        
            return HttpResponse(serializer.errors,status=406)
 
    def create(self, request, *args, **kwargs):
        
        serializer = ProductAdminSerializer(data=request.data)
        if serializer.is_valid():
            instance=serializer.save()
            headers = self.get_success_headers(serializer.data)
            context={
                'product':instance,
                'serializer':ProductAdminSerializer()
            }
            messages.success(request,"Product created successfully")
            return Response(context,template_name="admin/products_ad_success.html",content_type='text/html')
        else:
            context={
                'serializer':serializer
            }
           
            return Response(context,template_name="admin/products_add_form.html",content_type='text/html')
    
    def destroy(self,request,*args, **kwargs):
        # product=get_object_or_404(Product,pk=pk)
        # if product.orderitems.count()>0:
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
            return Response({'error':'Product cannot be deleted Since there are orders assossiated with this product'})
        instance = self.get_object()
        self.perform_destroy(instance)
        return redirect('admin-product-list')
    

class CategoryAdminViewSet(ModelViewSet):
    queryset=Main_Category.objects.annotate(products_count=Count('categories_products')).all()
    pagination_class=CategoryPagination
    serializer_class=CategoryAdminSerializer
    permission_classes=[IsAdminUser]
    renderer_classes=[TemplateHTMLRenderer]
    
    def get_template_names(self) -> list[str]:
        if self.action == 'retrieve':
            return ["admin/category.html"]
        return ["admin/categories-list.html"]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            messages.success(request,"Category added successfully")
            return redirect('main_category-list')
        else:
            errors=[f"{field} =>{error[0]}" for field,error in serializer.errors.items()]
          
            for error in errors:
                messages.error(request,error)
            return redirect('main_category-list')
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
     
        serializer=CategoryAdminSerializer(instance,data=request.data,partial=True)
        if serializer.is_valid():
           
            if not 'active' in serializer.validated_data:
                serializer.validated_data['active']=False
            serializer.save()
            
            messages.success(request,"Category updated successfully")
            return HttpResponse("success",status=200)
        else:
           
            return HttpResponse(serializer.errors,status=406)
        
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CategoryAdminSerializer(instance)
     
        context={
            'serializer':serializer,
            'category':serializer.data
            
        }
        return Response(context,status=status.HTTP_200_OK)
    
    def get_serializer_context(self):
        return {'request':self.request}

class BrandViewSet(ModelViewSet):
    queryset=Brand.objects.annotate(
        products_count=Count('brand_products')
        ).all()
    permission_classes=[IsAdminUser]
    pagination_class=BrandPagination
    serializer_class=BrandDetailsSerializer
    renderer_classes=[TemplateHTMLRenderer]
    
    
    
    def get_list(self):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
    
    
    def get_template_names(self) -> list[str]:
        if self.action in ['create','destroy']:
            return ["admin/brand-list.html"]
        elif self.action in ['list']:
            return ["admin/brand.html"]
        elif self.action in ['retrieve','update']:
            return ['admin/brand-edit.html']
            
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        context=self.get_list()
        if serializer.is_valid():
            self.perform_create(serializer)
            messages.success(request,"Brand created successfully")
            return Response(context)
        else:
            context['serializer']=serializer
            context['error']=True
            messages.error(request,"Error in Brand creation")
            return Response(context)
            # return render(request,template_name="admin/brand-list.html",context=context)
            
            
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        context={
                'serializer':serializer,
                'brand':serializer.data
            }
        return Response(context)
    def list(self, request, *args, **kwargs):
        context=self.get_list()

        return Response(context)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            messages.success(request,"Brand updated succesfully")
            return HttpResponse("success",status=200)
        else:
            context={
                'serializer':serializer
            }
            return HttpResponse(serializer.errors,status=406)
            
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        return Response(status=status.HTTP_204_NO_CONTENT)
        
    

class ProductImageViewSet(ModelViewSet,PageNumberPagination):
    serializer_class = ProductImageSerializer
    permission_classes=[IsAdminUser]
    # pagination_class=ProductImagePagination
    renderer_classes=[TemplateHTMLRenderer]
    

    def get_template_names(self) -> list[str]:
        if self.action == 'retrieve':
            return ["admin/product_image.html"]
        return ["admin/product_image-list.html"]
    
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # total_products=page.paginator.count
        # total_pages=total_products//page_size
        # if total_products % page_size != 0:
        #     total_pages += 1
        context={
            'serializer':self.get_serializer(),
            'product_id':self.kwargs['product_pk'],
            'results': serializer.data,
        }
        return Response(context)
    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance=serializer.save()
            headers = self.get_success_headers(serializer.data)
            context={
                'image':instance,
                'product_id':instance.product.id 
            }
            return Response(context,template_name="admin/product-newimage-row.html",content_type="text/html")
        else:
            return HttpResponse("error")
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProductImageSerializer(instance)
        
        context={
            'serializer':serializer,
            'image':serializer.data,
            'product_id':self.kwargs['product_pk'],
            
        }
       
        return Response(context,status=status.HTTP_200_OK)
    def update(self, request, *args, **kwargs):

        instance = self.get_object()

        serializer=ProductImageSerializer(instance,data=request.data,partial=True)
        if serializer.is_valid():

            serializer.save()
            
            messages.success(request,"Product image updated successfully")
            return HttpResponse("success",status=200)
        else:
            return HttpResponse(serializer.errors,status=406)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        messages.error(request,f"Image {instance.id} deleted successfully")
        return Response(template_name="admin/admin-nav-update.html",content_type="txt/html")


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'head', 'options']
    permission_classes=[IsAdminUser]
    renderer_classes=[TemplateHTMLRenderer]
    pagination_class=PageNumberPagination
    queryset=Order.objects.select_related('customer','address','applied_coupon').prefetch_related('items').all()
    
    
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UpdateAdminOrderSerializer
        return OrderSerializer


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.template_name="admin/order.html"
            response.content_type="text/html"
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    def update(self, request, *args, **kwargs):
        mode=request.data.get("mode",None)
        instance = self.get_object()
        items=OrderItem.objects.filter(order=instance)
        if mode=="order_item_update":
            item_id=request.data.get("item_id",None)
            try:
                item=items.get(id=item_id)
            except OrderItem.DoesNotExist as e:
                messages.error(request,e)
                return Response(template_name="admin/admin-nav-update.html",content_type='text/html')
            with transaction.atomic():
                if item.status == 'RR':
                    item.status="RA"
                    message=f"Return has been Approved for item {item.product.title}."
                    
                elif item.status== 'S':
                    item.status="D"
                    message=f"Item {item.product.title} has delivered successfully"
                elif item.status == 'P':
                    item.status='S'
                    message=f"Item {item.product.title} has shipped successfully"
                elif item.status=="RA":
                    item.status="RE"
                    product=Product.objects.get(id=item.product_id)
                    product.inventory+=item.quantity
                    product.save()
                    item_total=item.unit_price*item.quantity
                    items_propotion=item_total/instance.total
                    discount_amount=instance.total-instance.grand_total
                    item_discount=items_propotion*discount_amount
                    customer=Customer.objects.get(id=instance.customer_id)
                    transaction_obj=Transaction.objects.create(customer=customer,order=instance,amount=item_total-item_discount,transaction_type='refund')
                    customer.wallet_balance+=item_total-item_discount
                    customer.save()
                    message=f"Item {item.product.title} has returned successfully.Amount credited to Customer wallet"
            item.save()
            messages.info(request,message)
            item_serializer=OrderItemSerializer(item)
            return Response({"item":item_serializer.data,"order_id":instance.id},template_name="admin/order_item_row.html",content_type="text/html")
        return Response({'order':instance},template_name="admin/order-row.html",content_type="text/html")
    def retrieve(self, request, *args, **kwargs):
        mode=None
        if bool(request.GET):
            mode=request.GET['mode']
        instance = self.get_object()
        
        context={
            
            'order':instance.id
        }
        response = Response(context)
        if mode == "update":
            response.template_name="admin/order-form.html"
            response.content_type="text/html"
            return response
        
        else:
            serializer = self.get_serializer(instance)
            context={
                'order':serializer.data,
            }
            response = Response(context)
            response.template_name='admin/order-detail.html'
            response.content_type='text/html'
            return response

    
class CouponViewSet(ModelViewSet):
    permission_classes=[IsAdminUser]
    renderer_classes=[TemplateHTMLRenderer]
    pagination_class=PageNumberPagination
    serializer_class=CouponCUSerializer
    queryset=Coupon.objects.all()
    

        
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response= self.get_paginated_response(serializer.data)
            response.data['serializer']=CouponCUSerializer()
            response.template_name="admin/coupon-list.html"
            response.content_type="text/html"
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'coupon':serializer.data,
            'serializer':serializer
            },template_name="admin/coupon-edit.html",content_type="text/html")
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data=serializer.validated_data
            if data['valid_to']<=data['valid_from']:
                messages.error(request,"Valid_form cannot be greated than valid_to")
                context={
                'serializer':serializer
                }
                messages.error(request,"Please enter a valid Coupon details")
                return Response(context,template_name="admin/coupon-add-form.html",content_type='text/html')
            self.perform_create(serializer)
            messages.success(request,"Coupon saved Successfully")
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    'coupon':serializer.data,
                    'serializer':CouponCUSerializer()
                    },
                template_name="admin/coupon-row.html",
                content_type="text/html",
                status=status.HTTP_201_CREATED,
                headers=headers
                )
        else:
            context={
                'serializer':serializer
            }
            messages.error(request,"Please enter a valid Coupon details")
            return Response(context,template_name="admin/coupon-add-form.html",content_type='text/html')
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            messages.success(request,f"Coupoun {instance.id} Updated Successfully")
            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}
            context={
                'coupon':self.get_object(),
                
            }
            return Response(context,template_name="admin/coupon-row.html",content_type="text/html")
        else:
            messages.error(request,"Please enter a valid Coupon details")
            context={
                'coupon':instance,
                
            }
            return Response(context,template_name="admin/coupon-row.html",content_type="text/html")
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
class NavUpdateView(APIView):
    permission_classes=[IsAdminUser]
    renderer_classes=[TemplateHTMLRenderer]
    
    def get(self,request):
        return Response(template_name="admin/admin-nav-update.html",content_type="txt/html")
    
class SalesReportView(APIView):
    permission_classes=[IsAdminUser]
    renderer_classes=[TemplateHTMLRenderer]
    pagination_class=SalesReportPagination

    def get_orders(self, date_range, start_date, end_date):
        today = datetime.date.today()

        if date_range == 'daily':
            start_date = today - datetime.timedelta(days=1)
            end_date = today
        elif date_range == 'monthly':
            start_date = today - timedelta(days=30)
            end_date = today
        elif date_range == 'yearly':
            start_date = today - datetime.timedelta(days=365)
            end_date = today
        elif date_range == 'custom':
            if(start_date=='' or end_date==''):
                return None
            else:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                if start_date>end_date:
                    return None


        return Order.objects.filter(
                    placed_at__date__range=[start_date, end_date]
                ).select_related(
                    'customer__user', 'applied_coupon'
                    ).prefetch_related(
                        'items__product', 'items__product__images'
                    )

    def get_context_data(self, orders, date_range,start_date,end_date):
        total_sales = sum(order.total for order in orders)
        total_orders = len(orders) if isinstance(orders, list) else orders.count()
        return {
            'orders': orders,
            'total_sales': total_sales,
            'total_orders': total_orders,
            'date_range': date_range,
            'start_date':start_date,
            'end_date':end_date,
        }
   
   
    def generate_pdf(self, context):
        from io import BytesIO
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Title
        p.setFont("Helvetica-Bold", 20)
        p.drawString(100, height - 100, "Sales Report")

        # Date range
        p.setFont("Helvetica", 12)
        p.drawString(100, height - 140, f"Report: {context['date_range'].title()}")

        # Total sales and orders
        p.drawString(100, height - 160, f"Total Sales: {context['total_sales']}")
        p.drawString(100, height - 180, f"Total Orders: {context['total_orders']}")

        # Orders table
        p.drawString(100, height - 220, "Orders:")
        p.setFont("Helvetica", 10)
        p.drawString(100, height - 240, "Order ID")
        p.drawString(200, height - 240, "Customer")
        p.drawString(300, height - 240, "Total")
        p.drawString(400, height - 240, "Date")

        y = height - 260
        for order in context['orders']:
            p.drawString(100, y, str(order.id))
            p.drawString(200, y, order.customer.user.username)
            p.drawString(300, y, str(order.total))
            p.drawString(400, y, order.placed_at.strftime('%Y-%m-%d'))
            y -= 20
            if y < 40:  # check if we need a new page
                p.showPage()
                y = height - 40
                p.setFont("Helvetica", 10)

        p.save()
        buffer.seek(0)
        return buffer
    def export_to_pdf(self, context):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="sales_report.pdf"'

        buffer = self.generate_pdf(context)
        response.write(buffer.getvalue())
        buffer.close()

        return response
    
    def get(self,request):
        if not request.htmx:
            return Response(template_name="admin/sales_report_page.html",content_type="text/html")
        else:
            date_range = request.GET.get('date_range', 'daily')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            orders = self.get_orders(date_range, start_date, end_date)
            if orders== None:
                return HttpResponse('<p class="text-center text-danger">Please Choose a valid Date Range</p>')
            

            if 'export' in request.data:
                context = self.get_context_data(orders, date_range)
                return self.export_to_pdf(context)
            else:
                paginator = self.pagination_class()
                paginated_orders = paginator.paginate_queryset(orders, request)
                response= paginator.get_paginated_response(paginated_orders, date_range,start_date,end_date)
                if response==None:
                    return HttpResponse('<p class="text-center text-danger">No Orders in this query</p>')
                response.template_name="admin/sales_report.html"
                response.content_type="text/html"
                return response
    def post(self,request):
        date_range = request.data.get('date_range', 'daily')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        orders = self.get_orders(date_range, start_date, end_date)
        context = self.get_context_data(orders, date_range,start_date, end_date)
        return self.export_to_pdf(context)
        

