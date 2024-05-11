from .models import Main_Category,CartItem
from .serializers import CategorySerializer
from django.contrib.auth import get_user_model
from django.db.models.aggregates import Count
from django.contrib.sessions.models import Session
User=get_user_model()
def collection(request):
    # session_key=request.session.session_key
    # session=Session.objects.get(session_key=session_key)
    print(request.POST)
    # print(request.GET)
    # print(request.user.is_authenticated)
    # print(request.user)
    try:
        categories=Main_Category.objects.annotate(products_count=Count('categories_products')).filter(active=True)
        serializer=CategorySerializer(categories,many=True)
        return {'categories':serializer.data}
    except:
        return {'categories':None}

def userCustomer(request):
    if request.user.is_authenticated:
        try:
            user=User.objects.select_related('user').get(pk=request.user.id)
            cart=CartItem.objects.filter(customer=user.user)
            cart_count=cart.count()
            return {'user':user,'customer':user.user,'cart_count':cart_count}
        except Exception as e:
            print(e)
            return {'user':None,'customer':None}
        
    else:
        return {'user':None,'customer':None}
    
