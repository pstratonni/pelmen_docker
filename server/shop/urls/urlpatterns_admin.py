from django.urls import path
from shop.views import *

urlpatterns = [  # URLs for admin
    path('admin/manufacturers/', ManufacturerIsAdminAPIList.as_view(), ),
    path('admin/manufacturer/<int:pk>/', ManufacturerIsAdminAPIRUD.as_view(), ),
    path('admin/products/', ProductIsAdminAPIList.as_view(), ),
    path('admin/product/<int:pk>/', ProductIsAdminAPIRUD.as_view(), ),
    path('admin/orders/', OrderIsAdminAPIList.as_view(), ),
    path('admin/order/<int:pk>/', OrderAPIUpdate.as_view(), ),
    path('admin/order_item/<int:pk>/', OrderItemAPIUpdate.as_view(), ),
]
