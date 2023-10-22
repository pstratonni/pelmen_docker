from django.urls import path

from purchaser.views import PurchaserAPIRetrieve, PurchaserAPIList

urlpatterns = [
    # URL for purchaser
    path('purchaser/<int:pk>/', PurchaserAPIRetrieve.as_view()),
    # URL for admin
    path('admin/purchasers/', PurchaserAPIList.as_view())
]
