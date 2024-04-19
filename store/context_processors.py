from .models import Main_Category
from .serializers import CategorySerializer
from django.db.models.aggregates import Count
from django.contrib.sessions.models import Session

def collection(request):
    # session_key=request.session.session_key
    # session=Session.objects.get(session_key=session_key)
    
    print(request.POST)
    print(request.user.is_authenticated)
    print(request.user)
    try:
        categories=Main_Category.objects.annotate(products_count=Count('categories_products')).filter(active=True)
        serializer=CategorySerializer(categories,many=True)
        return {'categories':serializer.data}
    except:
        return None

def get_user(request):
    if request.user.is_authenticated:
        pass