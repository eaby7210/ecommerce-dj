from rest_framework import permissions
from django.contrib.auth import get_user_model

User=get_user_model()

class IsActive(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            user=User.objects.get(pk=request.user.id)
        except:
            user=None
            
        return bool(user and request.user.is_active)