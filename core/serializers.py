from djoser.serializers import UserSerializer as baseUserSerializer, UserCreatePasswordRetypeSerializer as baseUserCreateSerializer
from rest_framework import serializers


class UserCreateSerializer(baseUserCreateSerializer):
    phone = serializers.RegexField(
        regex=r'^\d{10}$', 
        error_messages={
            'invalid': 'Phone number must be 10 digits long with no spaces or hyphens.'
            }
    )
    class Meta(baseUserCreateSerializer.Meta):
        fields=['id','first_name','last_name','username','email','phone','password']
        
        
class UserSerializer(baseUserSerializer):
    class Meta(baseUserSerializer.Meta):
        fields=['id','first_name','last_name','username','email','phone']
        
