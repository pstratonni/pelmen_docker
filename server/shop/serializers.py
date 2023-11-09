from icecream import ic
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
    composition = serializers.SlugRelatedField(slug_field='title', read_only=True, many=True, )
    manufacturer = serializers.SlugRelatedField(slug_field='title', read_only=True)

    class Meta:
        model = Product
        exclude = ['categories']


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('title', 'counting')


class CartItemSerializer(serializers.ModelSerializer):

    # def create(self, validated_data):
    #     product = Product.objects.get(pk=validated_data.get('product', None).id)
    #     cart_item, _ = CartItem.objects.filter(cart=validated_data.get('cart')) \
    #         .update_or_create(product=product, defaults={**validated_data})
    #     cart_item.update_cart_item()
    #     cart = Cart.objects.get(pk=validated_data.get('cart', None).id)
    #     cart.update_cart()
    #     return cart_item

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

    # def create(self, validated_data):
    #     ic(validated_data)
    #     cart = Cart.objects.get(user=self.user)
    #     cart_items = CartItem.objects.filter(cart=cart)
    #     order = Order.obgects.create(user=self.user, defaults={**validated_data})
    #     for item in cart_items:
    #         if item.product.active:
    #             OrderItem.objects.create(order=order, quantity=item.quantity, price=item.price,
    #                                      product=item.product, discount=item.discount, total_price=item.total_price)
    #     order.update_order()
    #     cart.delete()
    #     Cart.objects.create(user=self.user)
    #     send_email_with_attach.delay(order.id)
    #     add_order_to_purchaser.delay(order.user.id)
    #     return order

    class Meta:
        model = Order
        fields = '__all__'
