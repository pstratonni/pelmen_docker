import base64
import os
from decimal import Decimal

from django_filters import rest_framework as filters
from django.contrib.auth.models import User
import requests
import json
from icecream import ic

from shop_server.tasks import send_email_with_attach, add_order_to_purchaser
from shop.models import Product, Cart, CartItem, OrderItem, Order, PayPal


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
        payment_id = data.json()['payment_id']
        approve_payment, price = verify_paypal_payment(payment_id, cart.id)
        paymen_id_from_db = PayPal.objects.get(cart_id=cart.id).payment_id
        if data.json()[
            'payment_type'] == 'PP' and not approve_payment and price != cart.total_price and paymen_id_from_db == payment_id:
            return [], False
        elif data.json()['payment_type'] == 'PP' and approve_payment:
            return [], False

        cart_items = CartItem.objects.filter(cart=cart)
        if not len(cart_items):
            raise
        data_dict = data.json()
        # for kye, value in data.items():
        #     data_dict[kye] = value
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


def make_pp_token():
    client_id = os.environ.get("PAYPAL_ID")
    secret = os.environ.get("PAYPAL_SECRET")
    token_url = os.environ.get("PAYPAL_BASE_URL") + '/v1/oauth2/token'

    token_payload = {"client_id": client_id,
                     "client_secret": secret,
                     "grant_type": "client_credentials"}

    token_headers = {'Accept': 'application/json', 'Accept-Language': 'de',
                     "Content-Type": "application/x-www-form-urlencoded",
                     "Authorization": "Basic {0}".format(
                         base64.b64encode((client_id + ":" + secret).encode()).decode())}

    token_response = requests.post(token_url, data=token_payload, headers=token_headers)
    return token_response.json()['access_token']


def create_order_paypal(user_id):
    access_token = make_pp_token()
    create_url = os.environ.get("PAYPAL_BASE_URL") + '/v2/checkout/orders'
    payment_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token,
    }

    user = User.objects.get(pk=user_id)
    cart = Cart.objects.get(user=user)

    payment_url = os.environ.get("PAYPAL_BASE_URL") + '/v2/checkout/orders'

    data = {"intent": "CAPTURE", "purchase_units": [{
        "amount": {"currency_code": "EUR", "value": str(cart.total_price)}}],
            "payment_source": {"paypal": {
                "experience_context": {"payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                                       "brand_name": "PFUNT INC", "locale": "de-DE", "landing_page": "LOGIN",
                                       "shipping_preference": "SET_PROVIDED_ADDRESS", "user_action": "PAY_NOW",
                                       "return_url": "https://example.com/returnUrl",  # fix urls later
                                       "cancel_url": "https://example.com/cancelUrl"}}}}

    payment_response = requests.post(payment_url, data=json.dumps(data), headers=payment_headers)
    if payment_response.status_code == 201:
        payment_id = payment_response.payment_response.json()['id']
        PayPal.objects.update_or_create(defult={"payment_id": payment_id}, user=user, cart_id=cart.id)
        approval_url = next(link['href'] for link in payment_response.json()['links'] if link['rel'] == 'approve')
        return True, approval_url
    else:
        return False, 'Failed to create PayPal payment.'


def verify_paypal_payment(payment_id, cart_id):
    access_token = make_pp_token()
    order_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token,
    }
    url = os.environ.get("PAYPAL_BASE_URL") + '/v2/checkout/orders/' + payment_id
    order_response = requests.get(url, headers=order_headers)
    if order_response.json()["status"] == "APPROVED" and payment_id == PayPal.objects.get(cart_id=cart_id).payment_id:
        return True, Decimal(order_response.json()["purchase_units"][0]["amount"]["value"])
    else:
        return False, None
