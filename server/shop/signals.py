from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from icecream import ic

from shop.models import Product

from shop_server.tasks import count_product


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
