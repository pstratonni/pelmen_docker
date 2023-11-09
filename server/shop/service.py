from django_filters import rest_framework as filters
from icecream import ic

from shop_server.tasks import send_email_with_attach, add_order_to_purchaser
from shop.models import Product, Cart, CartItem, OrderItem, Order


class ChartFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class ProductFilter(filters.FilterSet):
    category = ChartFilterInFilter(field_name='category', lookup_expr='in')

    class Meta:
        model = Product
        fields = ['category']


def create_order(user, data):
    try:
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        if not len(cart_items):
            raise
        data_dict = {}
        for kye, value in data.items():
            data_dict[kye] = value
        order = Order.objects.create(user=user, **data_dict)
        for item in cart_items:
            if item.product.active:
                OrderItem.objects.create(order=order, quantity=item.quantity, price=item.price,
                                         product=item.product, discount=item.discount, total_price=item.total_price)
        order.update_order()
        cart.delete()
        Cart.objects.create(user=user)
        send_email_with_attach.delay(order.id)
        add_order_to_purchaser.delay(order.user.id)
        return order, True
    except:
        return [], False


def create_cart_item(user__id: int, data):
    cart = Cart.objects.get(user__id=user__id)
    data_dict = {key: value for key, value in data.items()}
    if cart.id != int(data_dict['cart']):
        return None, False
    product = Product.objects.get(pk=data_dict['product'])
    cart_item, _ = CartItem.objects.filter(cart=cart).update_or_create(product=product, cart=cart,
                                                                       defaults={
                                                                           'quantity': int(data_dict['quantity'])})
    cart_item.update_cart_item()
    cart.update_cart()
    return cart_item, True
