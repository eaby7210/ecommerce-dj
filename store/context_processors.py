from .models import Main_Category
from .serializers import CategorySerializer
from django.contrib.auth import get_user_model
from django.db.models.aggregates import Count
from django.contrib.sessions.models import Session
User=get_user_model()
def collection(request):
    # session_key=request.session.session_key
    # session=Session.objects.get(session_key=session_key)
    print(request.POST)
    print(request.data)
    # print(request.user.is_authenticated)
    print(request.user)
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
            return {'user':user,'customer':user.user}
        except:
            return {'user':None,'customer':None}
        
    else:
        return {'user':None,'customer':None}