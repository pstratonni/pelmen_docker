from django.urls import path
from shop.views import *

urlpatterns = [
    # URLs for purchaser
    path('manufacturers/', ManufacturerAPIList.as_view(), ),
    path('manufacturer/<int:pk>/', ManufacturerAPIRetriever.as_view(), ),
    path('products/', ProductAPIList.as_view(), ),
    path('product/<int:pk>/', ProductAPIRetriever.as_view(), ),
    path('categories/', CategoryListView.as_view()),
    path('orders/', OrderAPIListCreate.as_view(), ),
    path('order/<int:pk>/', OrderAPIRetrieve.as_view(), ),
    path('order_item/', OrderItemAPICreate.as_view(), ),
    path('cart/', CartAPIRetrieveUpdateDestroy.as_view(), ),
    path('cart_item/create/', CartItemAPICreate.as_view(), ),
    path('cart_item/delete/<int:pk>/', CartItemAPIDestroy.as_view(), ),

    # URLs for admin
    path('admin/manufacturers/', ManufacturerIsAdminAPIList.as_view(), ),
    path('admin/manufacturer/<int:pk>/', ManufacturerIsAdminAPIRUD.as_view(), ),
    path('admin/products/', ProductIsAdminAPIList.as_view(), ),
    path('admin/product/<int:pk>/', ProductIsAdminAPIRUD.as_view(), ),
    path('admin/orders/', OrderIsAdminAPIList.as_view(),),
    path('admin/order/<int:pk>/', OrderAPIUpdate.as_view(),),
    path('admin/order_item/<int:pk>/', OrderItemAPIUpdate.as_view(),),
]
