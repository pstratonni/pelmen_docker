from rest_framework import serializers

from purchaser.models import *
from shop.models import Order, Product


class OrderSerializerForPurchaser(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('date_created', 'date_shipping', 'total_price', 'user')


class ProductSerialaizerForPurchaser(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('title', 'price', 'discount')
#


class PurchaserRetrieveSerializer(serializers.ModelSerializer):
    orders = OrderSerializerForPurchaser(many=True, read_only=True, required=False)
    favorite_product = ProductSerialaizerForPurchaser(many=True, read_only=True, required=False)

    class Meta:
        model = Purchaser
        fields = '__all__'


class PurchaserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchaser
        fields = ('id', 'user', 'name')
