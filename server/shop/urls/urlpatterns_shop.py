from django.urls import path
from shop.views import *

urlpatterns = [
    # URLs for purchaser
    path('manufacturers/', ManufacturerAPIList.as_view(), ),
    path('manufacturer/<int:pk>/', ManufacturerAPIRetriever.as_view(), ),
    path('products/', ProductAPIList.as_view(), ),
    path('product/<int:pk>/', ProductAPIRetriever.as_view(), ),
    path('categories/', CategoryListView.as_view()),
    path('orders/', OrderAPIList.as_view(), ),
    path('order/create/',OrderAPICreate.as_view(),),
    path('order/<int:pk>/', OrderAPIRetrieve.as_view(), ),
    path('order_item/', OrderItemAPICreate.as_view(), ),
    path('cart/', CartAPIRetrieveUpdateDestroy.as_view(), ),
    path('cart_item/create/', CartItemAPICreate.as_view(), ),
    path('cart_item/delete/<int:pk>/', CartItemAPIDestroy.as_view(), ),
]

