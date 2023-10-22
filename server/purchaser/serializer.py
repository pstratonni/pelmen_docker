from rest_framework import serializers

from purchaser.models import *
from shop.serializers import OrderSerializer


class PurchaserRetrieveSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Purchaser
        fields = '__all__'


class PurchaserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchaser
        fields = '__all__'
