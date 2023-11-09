from icecream import ic
from rest_framework import permissions


class IsOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or bool(request.user.is_staff)


class IsOwnerOrderOrCart(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        ic
        return obj.cart.user == request.user or bool(request.user.is_staff)

