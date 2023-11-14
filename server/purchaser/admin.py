from django.contrib import admin
from django.urls import reverse

from django.utils.http import urlencode
from django.utils.html import format_html
from purchaser.models import Purchaser


@admin.register(Purchaser)
class PurchaserAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'name', 'get_orders')
    search_fields = ('user__username__startswith',)
    list_per_page = 12
    readonly_fields = ('quantity_of_orders', 'sum_orders',)
    fields = (
        ('user', 'name'), ('address_street', 'address_home_number', 'address_ZIP', 'address_city'), 'phone_number',
        ('quantity_of_orders', 'sum_orders'), 'favorite_product')
    raw_id_fields = ('favorite_product',)

    # def order_quantity(self, instance):
    #     try:
    #         order = Order.objects.filter(user=instance.user)
    #         quantity = order.count()
    #         return format_html(
    #             f'<p style="font-weight:bold;">{quantity}</p>'
    #         )
    #     except:
    #         return 0
    #
    # order_quantity.short_description = 'Quantity of orders'
    #
    # def order_sum(self, instance):
    #     try:
    #         sum = Order.objects.filter(user=instance.user).aggregate(sum=Sum('total_price'))['sum']
    #         return format_html(
    #             f'<p style="font-weight:bold;">{sum}</p>'
    #         )
    #     except:
    #         return 0
    #
    # order_sum.short_description = 'Total price of all orders'

    @admin.display(description='Orders')
    def get_orders(self, instance):
        url = (
                reverse('admin:shop_order_changelist')
                + '?'
                + urlencode({'users__id__exact': f'{instance.user.id}'})
        )
        link = f'<a href="{url}">{instance.quantity_of_orders} Orders</a>'
        return format_html(link)

    @admin.display(description='Email')
    def get_email(self, instance):
        return instance.user.email
