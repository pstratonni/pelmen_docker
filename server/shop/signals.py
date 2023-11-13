from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from icecream import ic

from shop.models import Product, Shipment, Order, OrderItem, ShipmentItem

from shop_server.tasks import count_product, add_or_update_shipment_doc, send_email_with_attach


# recursion = False


# @receiver(post_save, sender=OrderItem)
# def update_order_items(sender, instance, created, **kwargs):
#     if not created:
#         global recursion
#         if recursion:
#             pass
#         else:
#             recursion = True
#             OrderItem.objects.get(pk=instance.id).update_price()
#             Order.objects.get(pk=instance.order.id).update_order()


@receiver(m2m_changed, sender=Product.categories.through, dispatch_uid='changed_categories')
def update_category(pk_set, **kwargs):
    for category_id in pk_set:
        count_product.delay(category_id)


# @receiver(post_save, sender=Product, dispatch_uid='changed_active')
# def update_active_product(instance, update_fields, created, **kwargs):
#     if not created:
#         try:
#             if 'active' in update_fields:
#                 for category in instance.categories.all().prefetch_related(
#                         Prefetch('products', queryset=Product.objects.all().only('pk'))):
#                     count_product.delay(category.id)
#         except:
#             pass

@receiver(post_save, sender=Shipment)
def create_shipment(sender, instance, created, **kwargs):
    if created:
        order_items = OrderItem.objects.filter(order=instance.order)
        shipment_product = {key.product.title: key.quantity for key in order_items}
        for shipment in instance.order.shipment.all():
            for item in shipment.shipment_items.all():
                shipment_product[item.product.title] -= item.quantity
        for item in order_items:
            if shipment_product[item.product.title] != 0:
                ShipmentItem.objects.create(shipment=instance, product=item.product,
                                            quantity=shipment_product[item.product.title])
        add_or_update_shipment_doc.delay(instance.id)


@receiver(post_save, sender=ShipmentItem)
def update_shipment_doc(sender, instance, created, **kwargs):
    add_or_update_shipment_doc.delay(instance.shipment.id)


@receiver(post_save, sender=OrderItem)
def update_order_invoces(instance, created, **kwargs):
    send_email_with_attach(instance.order.id)
