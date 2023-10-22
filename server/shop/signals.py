from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import F, Prefetch
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from shop.models import Cart, CartItem, Order, OrderItem, Tax, Product
from shop.service import create_pdf

from shop_server.tasks import count_product, send_email_with_attach


@receiver(post_save, sender=Order)
def create_order_items(sender, instance, created, **kwargs):
    if created:
        cart = Cart.objects.get(user=instance.user)
        try:
            cart_items = CartItem.objects.filter(cart=cart)
            for item in cart_items:
                if item.product.active:
                    OrderItem.objects.create(order=instance, quantity=item.quantity, price=item.price,
                                             product=item.product, discount=item.discount, total_price=item.total_price)

            order = Order.objects.get(pk=instance.id)
            order.update_order()

            order_items = OrderItem.objects.filter(order=order)
            tax = Tax.objects.all().annotate(tax_sum=(F('tax') / 100 * order.total_price * 100 // 1 / 100)).latest('id')
            # tax_sum = float(tax / 100 * order.total_price * 100 // 1 / 100)
            # tax = {
            #     'tax_cost': tax,
            #     'tax_sum': tax_sum,
            # }
            cart.delete()
            if instance.user:
                Cart.objects.create(user=instance.user)
            else:
                Cart.objects.create(ip=instance.ip)

            url, err = create_pdf(order, order_items, tax, )
            send_email_with_attach.delay(order, order_items, tax, url, err)
        except:
            pass


recursion = False


@receiver(post_save, sender=OrderItem)
def update_order_items(sender, instance, created, **kwargs):
    if not created:
        global recursion
        if recursion:
            pass
        else:
            recursion = True
            OrderItem.objects.get(pk=instance.id).update_price()
            Order.objects.get(pk=instance.order.id).prefetch_related('order_items').update_order()


repeat = True


@receiver(m2m_changed, sender=Product.categories.through, dispatch_uid='changed_categories')
def update_category(sender, instance, pk_set, **kwargs):
    global repeat
    if repeat:
        repeat = False
        for category_id in pk_set:
            count_product.delay(category_id)
    else:
        repeat = True


@receiver(post_save, sender=Product, dispatch_uid='changed_active')
def update_active_product(instance, update_fields, created, **kwargs):
    if not created:
        if 'active' in update_fields:

            for category in instance.categories.all().prefetch_related(
                    Prefetch('products', queryset=Product.objects.all().only('pk'))):
                count_product.delay(category.id)
