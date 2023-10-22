from django.contrib import admin
from django.db.models import Count, Sum
from django.utils.html import format_html

from purchaser.models import Purchaser
from shop.models import Order


@admin.register(Purchaser)
class PurchaserAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'name')
    search_fields = ('user',)
    list_per_page = 12
    readonly_fields = ('order_quantity', 'order_sum',)
    fields = (('user', 'name'), ('address_street', 'address_home_number', 'address_ZIP', 'address_city'), 'phone_number',
              ('order_quantity', 'order_sum'), 'favorite_product')
    raw_id_fields = ('favorite_product',)

    def order_quantity(self, instance):
        try:
            order = Order.objects.filter(user=instance.user)
            quantity = order.count()
            return format_html(
                f'<p style="font-weight:bold;">{quantity}</p>'
            )
        except:
            return 0

    order_quantity.short_description = 'Quantity of orders'

    def order_sum(self, instance):
        try:
            sum = Order.objects.filter(user=instance).aggregate(sum=Sum('total_price'))['sum']
            return format_html(
                f'<p style="font-weight:bold;">{sum}</p>'
            )
        except:
            return 0

    order_sum.short_description = 'Total price of all orders'

    @admin.display(description='Email')
    def get_email(self, instance):
        return instance.user.email
