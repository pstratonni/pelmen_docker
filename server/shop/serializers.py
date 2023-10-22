from rest_framework import serializers

from shop.models import *


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = "__all__"


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('title', 'price', 'id', 'image')


class ProductDetailSerializer(serializers.ModelSerializer):
    composition = serializers.SlugRelatedField(slug_field='title', read_only=True, many=True,)

    class Meta:
        model = Product
        fields = '__all__'


class CategoryListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        product = Product.objects.get(pk=validated_data.get('product', None).id)
        cart_item, _ = CartItem.objects.filter(cart=validated_data.get('cart')) \
            .update_or_create(product=product, price=product.price,
                              total_price=validated_data.get('quantity') * (product.price - product.discount),
                              discount=product.discount,
                              defaults={**validated_data})
        return cart_item

    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    cart_items = CartItemSerializer(many=True, required=False)

    class Meta:
        model = Cart
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    # def create(self, validated_data):
    #     product = Product.objects.get(pk=validated_data.get('product', None).id)
    #     order_item, _ = OrderItem.objects.filter(cart=validated_data.get('order')) \
    #         .update_or_create(
    #         total_price=validated_data.get('quantity') * (product.price - validated_data.get('discount')),
    #         defaults={**validated_data})
    #     return order_item

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderRetrieveSerializer(serializers.ModelSerializer):
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    order_items = OrderItemSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Order
        fields = '__all__'
