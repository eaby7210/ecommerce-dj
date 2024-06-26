from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models.aggregates import Count
from django.db.models import Prefetch
from datetime import date
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet,ReadOnlyModelViewSet
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Product,Brand,Transaction
from .serializers import *
from .filter import *
import datetime


from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO


  
class ProductViewset(ProductPagination,ReadOnlyModelViewSet):
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, SearchFilter,OrderingFilter]
    filterset_fields=['category']
    search_fields = ['title']
    ordering_fields = ['title','unit_price', 'last_update']
    renderer_classes=[TemplateHTMLRenderer]
    
    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return ProductCartSerializer
        else:
            return ProductSerializer
    def get_serializer_context(self):
        return {'request':self.request}
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            customer = Customer.objects.get(user=self.request.user)
            return Product.objects.annotate(
                            num_images=Count('images')
                        ).filter(
                            active=True,
                            num_images__gt=0
                        ).order_by('id').prefetch_related(
                            'images',
                            Prefetch(
                                'cartitem_set',
                                queryset=CartItem.objects.only('id', 'quantity').filter(customer=customer),
                                to_attr='cart_items'
                            ),
                            Prefetch(
                                'wish_product',
                                queryset=WishList.objects.only('id').filter(customer=customer),
                                to_attr='wishlist_items'
                            )
                        ).select_related('brand', 'category')
        return Product.objects.annotate(
                            num_images=Count('images')
                        ).prefetch_related('images').\
            select_related('brand').select_related('category').\
                filter(num_images__gt=0,active=True).order_by('id')
    
    def get_template_names(self) -> list[str]:
        if self.action == 'list':
            if self.request.htmx:
                return ["app/products-list.html"]
            else:
                return ["app/products.html"]
        else:
            return ["app/product_page.html"]
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset,request=request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def retrieve(self, request, *args, **kwargs):
        
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            context={
                'product':serializer.data,
            }
            return Response(context)
        except:
            messages.info(request,"That Product is currently unavailable")
            return redirect('product_list')
    

#not completed
class BrandViewSet(ReadOnlyModelViewSet):
    queryset=Brand.objects.annotate(products_count=Count('brand_products')).filter(active=True)
    pagination_class=CustomPagination
    serializer_class=BrandDetailsSerializer
    permission_classes=[AllowAny]
    renderer_classes=[TemplateHTMLRenderer]
    
    def get_template_names(self) -> list[str]:
        if self.action == 'retrieve':
            return ["app/brand.html"]
        return ["app/brandslist.html"]
    
    
    
    def get_serializer_context(self):
        return {'request':self.request}
    

#not completed  
class CategoryViewSet(ReadOnlyModelViewSet):
    queryset=Main_Category.objects.annotate(products_count=Count('categories_products')).filter(active=True)
    pagination_class=CustomPagination
    serializer_class=CategorySerializer
    permission_classes=[AllowAny]
    renderer_classes=[TemplateHTMLRenderer]
    
    def get_template_names(self) -> list[str]:
        if self.action == 'retrieve':
            return ["app/category.html"]
        return ["app/categorylist.html"]
    
    
    
    def get_serializer_context(self):
        return {'request':self.request}
    

class CartViewSet(ModelViewSet):
    permission_classes=[IsAuthenticated]
    renderer_classes=[TemplateHTMLRenderer]
    
    # def get_template_names(self) -> list[str]:
    #     if self.action in ['list']:
    #         return ["app/cart.html"]
        
    def get_customer_id(self):
        return Customer.objects.only('id').get(user_id=self.request.user.id)
    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'customer_id':self.get_customer_id().id
        }
    def get_serializer_class(self):
        if self.action in ['list','retrieve']:
            return CartSerializer
        return CartCUSerializer
    def get_queryset(self):
        customer_id=self.get_customer_id().id
        return CartItem.objects.select_related('product').filter(customer=customer_id)
    def list(self, request, *args, **kwargs):
        if CartItem.objects.filter(customer=self.get_customer_id()).count()==0:
            messages.error(request,"Cart is Empty,Please add products to view the cart.")
            return redirect('u-product-list')
        mode=None
        if bool(request.GET):
            mode=request.GET['mode']
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response= self.get_paginated_response(serializer.data)
            response.content_type="text/html"
            if mode is None:
                response.template_name="app/cart.html"
                return response
            elif mode =="checkout":
                response.template_name="app/checkout.html"
                return response
                
            

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        data={key: value for key, value in request.data.items()}
        mode=data.pop('mode')
        page=data.pop('in')
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            instance,message=serializer.save(mode=mode)
            cartserializer=CartSerializer(instance=instance)
            cart=cartserializer.data
            messages.error(request,message=message)
            if page== 'list':
                context={
                "item":cart
                }
                response=Response(context,template_name="app/cart-add-listpage.html",content_type="text/html")
                return response
            elif page == 'detail':
                context={
                "item":cart
                }
                response=Response(context,template_name="app/cart-add-detailpage.html",content_type="text/html")
                return response
            elif page =='wishlist':
                if instance==None:
                    wishitem=WishList.objects.select_related('product').get(
                        customer=self.get_customer_id(),
                        product_id=serializer.data['product_id'])
                    results=WishListSerializer(wishitem)
                    context={
                        'item':results.data
                    }
                    return Response(context,template_name="app/wishitem.html",content_type="text/html")
                wishitem=WishList.objects.get(
                    customer=self.get_customer_id(),
                    product_id=serializer.data['product_id']
                    )
                wishitem.delete()
                return Response(template_name="app/nav-update.html",content_type='text/html')
            
        else:
            messages.error(request,"Error in Adding to cart")
            context={
                "item":instance
            }
            return Response(context,template_name="app/cart-list.html",content_type="text/html")
            
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        messages.warning(request,f"{instance.product.title} has been removed from cart")
        self.perform_destroy(instance)
        return Response(template_name="app/nav-update.html",content_type="text/html")
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        context={
            "serializer":serializer,
            "item":serializer.data
        }
        return Response(context,template_name="app/cart-del.html",content_type="text/html")
    
    def update(self, request, *args, **kwargs):
        data={key: value for key, value in request.data.items()}
        mode=data.pop('mode')
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            instance,message=serializer.save(mode=mode)
            cartserializer=CartSerializer(instance=instance)
            cart=cartserializer.data
            messages.info(request,message=message)
            context={
                "item":cart
            }
            response=Response(context,template_name="app/cart-list.html",content_type="text/html")
            return response
        else:
            messages.error(request,"Error in updating quantity")
            context={
                "item":instance
            }
            return Response(context,template_name="app/cart-list.html",content_type="text/html")

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'head', 'options']
    renderer_classes=[TemplateHTMLRenderer]
    permission_classes=[IsAuthenticated]
    
    def get_customer(self):
       return Customer.objects.only('id','wallet_balance').get(user_id=self.request.user.id)
    
    def get_queryset(self):  
        return Order.objects.select_related(
            'address',
            'applied_coupon'
            ).prefetch_related(
                'razor_orders',
                Prefetch('items',queryset=OrderItem.objects.select_related('product')),
                ).filter(customer=self.get_customer())
    
    def get_serializer_class(self):
        if self.action in ['create','update']:
            return CreateOrderSerializer
        elif self.action in ['list','retrieve']:
            return OrderSerializer
    
    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'customer':self.get_customer()
        }
        
    def razor_pay_reponse(self,razorpay_obj,message,ptotal):
        if razorpay_obj==None:
            messages.error(self.request,message)
            return redirect(reverse('home'))
        rzr_serializer=RazorSerializer(razorpay_obj)
        messages.warning(self.request,message)
        context={
            'razorpay_id':settings.RAZORPAY_ID,
            'razorpay':rzr_serializer.data,
            'ptotal':ptotal
        }
        return Response(context)
    
   
    def list(self, request, *args, **kwargs):
        mode=request.GET.get('mode',None)
        queryset = self.filter_queryset(self.get_queryset())
        
        if mode=="profile":
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response= self.get_paginated_response(serializer.data)
                response.template_name="app/order-list.html"
                response.content_type="text/html"
                return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        mode=request.GET.get('mode',None)
        instance = self.get_object()
        serializer = OrderSerializer(instance)
        if mode=="pdfgen":
            # Generate PDF invoice
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []

            # Title
            title = "Invoice"
            generation_date = datetime.datetime.now().strftime("%Y-%m-%d")
            title_paragraph = Paragraph(f"{title}<br/>Date: {generation_date}", getSampleStyleSheet()['Title'])
            elements.append(title_paragraph)
            elements.append(Spacer(1, 0.5 * inch))

            # Order details
            elements.append(Paragraph(f"Order ID: {instance.id}", getSampleStyleSheet()['BodyText']))
            elements.append(Paragraph(f"Customer: {instance.customer.user.username}", getSampleStyleSheet()['BodyText']))
            address = instance.address
            address_string = f"{address.name}, {address.city}, {address.state}, {address.pin}, {address.other_details}"

            elements.append(Paragraph(f"Address: {address_string}", getSampleStyleSheet()['BodyText']))
            elements.append(Spacer(1, 0.5 * inch))

            # Order items
            items_data = [['Product', 'Quantity', 'Unit Price', 'Total Price']]
            for item in instance.items.all():
                items_data.append([
                    item.product.title,
                    item.quantity,
                    item.unit_price,
                    item.unit_price * item.quantity
                ])
            items_table = Table(items_data, hAlign='LEFT')
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(Paragraph("Order Items", getSampleStyleSheet()['Heading2']))
            elements.append(items_table)
            elements.append(Spacer(1, 0.5 * inch))

            # Order totals
            elements.append(Paragraph(f"Total: {instance.total}", getSampleStyleSheet()['BodyText']))
            elements.append(Paragraph(f"Total Discount: {instance.total_discount}", getSampleStyleSheet()['BodyText']))
            elements.append(Paragraph(f"Grand Total: {instance.total - instance.total_discount}", getSampleStyleSheet()['BodyText']))

            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            return HttpResponse(buffer, content_type='application/pdf')
        context={
            'order':serializer.data,
        }
        return Response(context,template_name='app/order-summary.html',content_type="text/html")
    
    def create(self, request, *args, **kwargs):
        customer=self.get_customer()
        if CartItem.objects.filter(customer=customer).count()==0:
            messages.error(request,"PLease add products to Cart to order")
            return redirect('u-product-list')
        
        data={key: value for key, value in request.data.items()}
        payment_method=data.pop('payment-method',None)
        coupon=data.pop('coupon',None)
        
        if payment_method is None:
            return Response({'detail': "Error while processing Payment please try again.(payment method)"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CreateOrderSerializer(
            data=data,context={'customer':customer}
            )
        
        if serializer.is_valid():
            if payment_method=="cod":
                message,order,total = serializer.save(coupon=coupon,payment_method=payment_method)
                if order==None:
                    messages.error(request,message)
                    return redirect(reverse('checkout'))
                elif total==None:
                    messages.success(request,message)
                    return redirect('u-order-detail',pk=order.id)
                    
                serializer = OrderSerializer(order)
                messages.success(request,message)
                context={
                    'order':serializer.data,
                    'total':total
                }
                return Response(context,template_name='app/order-summary.html',content_type='text/html')
            elif payment_method=="rzr":
                message,razorpay_obj,ptotal = serializer.save(coupon=coupon,payment_method=payment_method)
                if razorpay_obj==None:
                    messages.error(request,message)
                    return redirect(reverse('checkout'))
                elif ptotal==None:
                    messages.success(request,message)
                    return redirect('u-order-detail',pk=razorpay_obj.order.id)
                response=self.razor_pay_reponse(razorpay_obj,message,ptotal)
                response.template_name="app/payment.html"
                response.content_type='text/html'
                return response
                
        else:
            HttpResponse("Error on creating order")
        
    
    def update(self, request, *args, **kwargs):
        mode=request.data.get('mode',None)
        
        instance = self.get_object()
        orderitems=instance.items
        with transaction.atomic():
            if mode=='retry_rzr':
                pk=self.kwargs.get('pk')
                razorpay_obj=RazorpayOrders.objects.select_related('order').get(order_id=pk)
                message="Please complete your payment through RazorPay gateway"
                response=self.razor_pay_reponse(razorpay_obj,message,razorpay_obj.order.grand_total)
                response.template_name="app/payment-section.html"
                response.content_type='text/html'
                return response
            elif mode=='cancel':
                if instance.payment_status=='C':
                    customer=self.get_customer()
                    transaction_obj=Transaction.objects.create(customer=customer,order=instance,amount=instance.payed_total,transaction_type='refund')
                    customer.wallet_balance=instance.grand_total
                    instance.payed_total=0
                    customer.save()
                for item in orderitems.all():
                    product=item.product
                    product.inventory+=item.quantity
                    product.save()    
                instance.order_status='CA'
                instance.save()
                messages.info(request,f"Order{instance.id} cancelled successfully")
            
            elif mode == "return":
                itemid = request.data.get('itemid', None)
             
                try:
                    item = OrderItem.objects.get(id=itemid)
                 
                    item.status = 'RR'
                    item.save()
                    item.refresh_from_db()
                   
                    messages.warning(request, f"Requested for return on item {str(item)}")
                except Exception as e:
                    messages.error(request, f"Could not process return for item {itemid}",e)

        instance.refresh_from_db()
        order =instance
        serializer = OrderSerializer(order)
        
        return Response(
            {"order": serializer.data},
            template_name="app/order-summary-card.html",
            content_type="text/html"
        )
            

    
class WhishListViewSet(ModelViewSet):
    renderer_classes=[TemplateHTMLRenderer]
    permission_classes=[IsAuthenticated]
    pagination_class=PageNumberPagination
    
    def get_customer_id(self):
        return Customer.objects.only('id').get(user_id=self.request.user.id)
    def get_serializer_class(self):
        if self.action == 'list':
            return WishListSerializer
        elif self.action in ['create','destroy']:
            return CreateWhishSerializer
    def get_queryset(self):
        return WishList.objects.select_related('product').filter(customer=self.get_customer_id())
    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'customer':self.get_customer_id()
        }
    
    
    def list(self, request, *args, **kwargs):
        
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response= self.get_paginated_response(serializer.data)
            if request.htmx:
                response.template_name="app/wishlist-items.html"
            else:
                response.template_name="app/wishlist.html"
                response.content_type='text/html'
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    def create(self, request, *args, **kwargs):
        data={key: value for key, value in request.data.items()}
        mode=data.pop('mode',None)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            instance,message,status=serializer.save()
            headers = self.get_success_headers(serializer.data)
            messages.info(request,message)
            if mode=="product_list":
                context={
                    'status':status,
                    'product_id':data['product_id']
                }
                return Response(context,template_name='app/wishlist-plist.html',content_type="text/html")
            elif mode=='product_page':
                context={
                    'status':status,
                    'product_id':data['product_id']
                }
                return Response(context,template_name='app/wishlist-ppage.html',content_type="text/html")
            elif mode=='wishlist':
                return Response(template_name='app/nav-update.html',content_type='text/html')
                # if status=="removed":
                #     return
                # elif status=="added":
                #     return
        else:
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

  
class CheckCoupon(APIView):
    renderer_classes=[TemplateHTMLRenderer]
    permission_classes=[IsAuthenticated]
    
    def delete(self,request,*args, **kwargs):
        context={
        'total':"₹"+request.data['total']
            
        }
        messages.info(request,"Coupon Removed Sucessfully")
        return Response(context,template_name="app/coupon-form.html",content_type="text/html")
    
    def post(self,request,*args, **kwargs):
        coupon=request.data['coupon'].strip()
        total=Decimal(request.data['grand_total'])
        try:
            coupon=Coupon.objects.get(code=coupon,active=True) 
            today = date.today()
            if not (coupon.valid_from <= today <= coupon.valid_to):
                messages.warning(request, "This coupon is expired or not yet valid.")
                return Response(template_name="app/coupon-form.html", content_type="text/html")
            discount_amt=total*(coupon.discount/Decimal(100))
            final_total=total-discount_amt
            context={
                'coupon':coupon,
                'total':total,
                'discount_amt':discount_amt,
                'final_total':final_total
            }
            messages.success(request,f"Coupon {coupon.name} applied successfully.")
            return Response(context,template_name="app/coupon-details.html",content_type='text/html')
        except Coupon.DoesNotExist:
            messages.warning(request,"Please Enter a valid Coupon code")
            context={
                'total':total,
                "htmx":request.htmx
            }
            return Response(context,template_name="app/coupon-form.html",content_type="text/html")
        
    
class CheckoutView(APIView):
    renderer_classes=[TemplateHTMLRenderer]
    permission_classes=[IsAuthenticated]
    
    def get_customer(self):
        return Customer.objects.only('id').get(user_id=self.request.user.id)
    
    def get(self,request,*args,**kwargs):
        cartitems=CartItem.objects.select_related('product').filter(customer=self.get_customer())
        if cartitems.count()<=0:
            messages.warning(request,"Cart is empty")
            return redirect(reverse('home'))
        for item in cartitems:
            if item.product.inventory==0 or item.quantity>item.product.inventory:
                messages.warning(request,"There are Products that is Out of stock or more than that of stock")
                return redirect(reverse('u-cart-list'))
        serializer=CartSerializer(cartitems,many=True)
        totals=[item['total_price'] for item in serializer.data]
        context={
            'cartitems':serializer.data,
            'grand_total':sum(totals)
        }
        
        return Response(context,template_name='app/checkout.html',content_type='text/html')
 
 
@csrf_exempt       
def payment(request):
    from django.db import transaction
    if request.method=="POST":
        razorpay_payment_id=request.POST['razorpay_payment_id']
        razorpay_order_id=request.POST['razorpay_order_id']
        razorpay_signature=request.POST['razorpay_signature']
        with transaction.atomic():
            try:
                
                rzr=RazorpayOrders.objects.prefetch_related('order').get(id=razorpay_order_id)
                customer=Customer.objects.only('id','wallet_balance').get(user_id=request.user.id)
                if rzr.order.payment_status=='C':
                    customer.wallet_balance+=rzr.order.grand_total
                    messages.warning(request,"Order payment seems to be already Completed. Amount will be credited to your wallet.")
                    return redirect(reverse('u-order-detail',args=[rzr.order.id])) 
                rzr.rzr_payment_id=razorpay_payment_id
                rzr.rzr_signature=razorpay_signature
                rzr.order.order_status='PL'
                rzr.order.payed_total=rzr.order.grand_total
                rzr.order.payment_status='C'
                transaction_obj=Transaction.objects.create(customer=customer,order=rzr.order,amount=rzr.order.grand_total,transaction_type='order')
                rzr.order.save()
                rzr.save()
                return redirect(reverse('u-order-detail',args=[rzr.order.id]))
            except:
                return HttpResponse("Error in placing the order")
            
    
class TransactionViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    renderer_classes=[TemplateHTMLRenderer]

    def get_queryset(self):
        return Transaction.objects.filter(customer__user=self.request.user).order_by('-created_at')

    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response= self.get_paginated_response(serializer.data)
            response.template_name="app/transaction_list.html"
            response.content_type="txt/html"
            return response
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

