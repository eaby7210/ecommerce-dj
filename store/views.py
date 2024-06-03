from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models.aggregates import Count
from django.db.models import Prefetch
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
import pprint
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Product,Brand,Address
from .serializers import *
from .filter import *

class ProductListView(APIView, PageNumberPagination):
    """
    API view to get a paginated list of active products with HTML template rendering.
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'app/products.html'  # Assuming template location
    page_size=20
    # filterset_class = ProductFilter
    def get(self, request, format=None):
        """
        Get a list of active products.
        """
        if request.user.is_authenticated:
            customer = Customer.objects.get(user=self.request.user)
            queryset=Product.objects.prefetch_related(
                'images',
                Prefetch(
                    'cartitem_set',queryset=CartItem.objects.only('id','quantity').filter(customer=customer),
                         to_attr='cart_items'
                         ),
                 Prefetch(
                        'wish_product',
                        queryset=WishList.objects.only('id').filter(customer=customer),
                        to_attr='wishlist_items'
                    )
                ).select_related('brand', 'category').filter(active=True)
        else:
            queryset = Product.objects.prefetch_related('images').select_related('brand').select_related('category').filter(active=True)
        page = self.paginate_queryset(queryset,request)
        if page is not None:
            if request.user.is_authenticated:
                serializer=ProductCartSerializer(page, many=True, context={'request': request})
            else:
                serializer = ProductSerializer(page, many=True, context={'request': request})
            # pprint.pprint(serializer.data)
            total_products=self.page.paginator.count
            page_size=self.get_page_size(request)
            total_pages=total_products//page_size
            if total_products % page_size != 0:
                total_pages += 1
            
            context={
                'total_pages':total_pages,
                'page_number':self.get_page_number(request,paginator=page),
                'page_size':page_size,
                'count': total_products,
                'next': f'/product/?page={self.page.number+1}',
                'previous': f'/product/?page={self.page.number-1}',
                'results': serializer.data,
            }
            # pprint.pprint("first:",context['next'])
            return Response(context, status=status.HTTP_200_OK)
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
  
  
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
            return Product.objects.prefetch_related(
                'images',
                Prefetch(
                    'cartitem_set',queryset=CartItem.objects.only('id','quantity').filter(customer=customer),
                         to_attr='cart_items'
                         ),
                Prefetch(
                        'wish_product',
                        queryset=WishList.objects.only('id').filter(customer=customer),
                        to_attr='wishlist_items'
                    )
                ).select_related('brand', 'category').filter(active=True)
        return Product.objects.prefetch_related('images').\
            select_related('brand').select_related('category').\
                filter(active=True)
    
    def get_template_names(self) -> list[str]:
        if self.action == 'list':
            return ["app/products-list.html"]
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
            return redirect('product_list')
        mode=None
        if bool(request.GET):
            print(request.GET)
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
        print(request.data)
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
                    print(context)
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
        print(data)
        mode=data.pop('mode')
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            instance,message=serializer.save(mode=mode)
            cartserializer=CartSerializer(instance=instance)
            cart=cartserializer.data
            print(cart)
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
        instance = self.get_object()
        serializer = OrderSerializer(instance)
        context={
            'order':serializer.data,
        }
        return Response(context,template_name='app/order-summary.html',content_type="text/html")
    
    def create(self, request, *args, **kwargs):
        customer=self.get_customer()
        if CartItem.objects.filter(customer=customer).count()==0:
            messages.error(request,"PLease add products to Cart to order")
            return redirect('product_list')
        
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
                message,order = serializer.save(coupon=coupon,payment_method=payment_method)
                if order==None:
                    messages.error(request,message)
                    return redirect(reverse('home'))
                    
                serializer = OrderSerializer(order)
                messages.success(request,message)
                context={
                    'order':serializer.data
                }
                return Response(context,template_name='app/order-summary.html',content_type='text/html')
            elif payment_method=="rzr":
                message,razorpay_obj,ptotal = serializer.save(coupon=coupon,payment_method=payment_method)
                response=self.razor_pay_reponse(razorpay_obj,message,ptotal)
                response.template_name="app/payment.html"
                response.content_type='text/html'
                return response
                
        else:
            print(serializer.errors)
        
    
    def update(self, request, *args, **kwargs):
        mode=request.data.get('mode',None)
        print(request.data,mode)
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
                    instance.payed_total
                    customer=self.get_customer()
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
                print(f"Attempting to return item with id: {itemid}")
                try:
                    item = OrderItem.objects.get(id=itemid)
                    print(f"Current item status before update: {item.status}")
                    item.status = 'RR'
                    item.save()
                    item.refresh_from_db()
                    print(f"Item status after update: {item.status}")
                    messages.warning(request, f"Requested for return on item {str(item)}")
                except Exception as e:
                    print(f"Error updating item status: {e}")
                    messages.error(request, f"Could not process return for item {itemid}")

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
        print(request.data)
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
    
    def delete(self,request,*args, **kwargs):
        context={
        'total':"$"+request.data['total']
            
        }
        messages.info(request,"Coupon Removed Sucessfully")
        return Response(context,template_name="app/coupon-form.html",content_type="text/html")
    
    def post(self,request,*args, **kwargs):
        print(request.data)
        coupon=request.data['coupon'].strip()
        total=Decimal(request.data['grand_total'])
        try:
            coupon=Coupon.objects.get(code=coupon,active=True) 
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
            return Response(template_name="app/coupon-form.html",content_type="text/html")
        
    
class CheckoutView(APIView):
    renderer_classes=[TemplateHTMLRenderer]
    
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
    if request.method=="POST":
        print(request.POST)
        razorpay_payment_id=request.POST['razorpay_payment_id']
        razorpay_order_id=request.POST['razorpay_order_id']
        razorpay_signature=request.POST['razorpay_signature']
        try:
            
            rzr=RazorpayOrders.objects.prefetch_related('order').get(id=razorpay_order_id)
            if rzr.order.payment_status=='C':
                customer=Customer.objects.only('id','wallet_balance').get(user_id=request.user.id)
                customer.wallet_balance+=rzr.order.grand_total
                messages.warning(request,"Order payment seems to be already Completed. Amount will be credited to your wallet.")
                return redirect(reverse('u-order-detail',args=[rzr.order.id])) 
            rzr.rzr_payment_id=razorpay_payment_id
            rzr.rzr_signature=razorpay_signature
            rzr.order.order_status='PL'
            rzr.order.payed_total=rzr.order.grand_total
            rzr.order.payment_status='C'
            rzr.order.save()
            rzr.save()
            return redirect(reverse('u-order-detail',args=[rzr.order.id]))
        except:
            return HttpResponse("Error in placing the order")
        
        

    
        
    
