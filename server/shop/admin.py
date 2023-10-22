from django.contrib import admin
import calendar
import datetime

import dateutils
from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.contrib.admin.sites import AdminSite

from shop.models import *
from purchaser.models import Purchaser

AdminSite.site_header = 'Pelmeni in Hamburg'

admin.site.register(Manufacturer)

admin.site.register(Tax)


class DateCommentFilter(admin.SimpleListFilter):
    title = 'Bestellungsdate'
    parameter_name = 'date_created'

    def lookups(self, request, model_admin):
        filter = []
        orders = Order.objects.order_by('date_created')
        dates = {}
        for order in orders:
            if order.date_created.strftime('%B %Y') in dates.keys():
                continue
            _, last_day = calendar.monthrange(order.date_created.year, order.date_created.month)
            date_value = order.date_created.strftime(f"%Y,%m,{last_day},23,59,59")
            dates[order.date_created.strftime('%B %Y')] = ''
            filter.append((date_value, order.date_created.strftime('%B %Y')))
        return filter

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        value = tuple(map(int, self.value().split(',')))
        value = datetime.datetime(*value)
        return queryset.filter(
            date_created__gte=(value - dateutils.relativedelta(months=1) + datetime.timedelta(seconds=1)),
            date_created__lte=value)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('colored_title', 'price', 'discount', 'active', 'date_created',)
    list_per_page = 16
    search_fields = ('title',)
    list_filter = ('active',)
    date_hierarchy = 'date_created'
    list_display_links = ('colored_title', 'discount')
    list_editable = ('active',)
    raw_id_fields = ('composition',)

    def save_model(self, request, obj, form, change):
        update_fields = set()
        if change:
            for key, value in form.cleaned_data.items():
                # assuming that you have ManyToMany fields that are called groups and user_permissions
                # we want to avoid adding them to update_fields
                if key in ['user_permissions', 'groups', 'categories', 'composition', 'id']:
                    continue
                if value != form.initial[key]:
                    update_fields.add(key)

        obj.save(update_fields=update_fields)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'id', 'total_amount', 'total_price')
    search_fields = ('user',)
    date_hierarchy = 'date_created'
    readonly_fields = ('cart_items',)

    def cart_items(self, instance):
        items = instance.cart_items.all()
        render = '<tr><td>Title of product</td><td>Quantity</td><tr>'
        for line in items:
            render += f'<tr><td>{line.product}</td><td style="text-align:center">{line.quantity}</td><td>{line.id}</td></tr>'
        render_html = "<table style=\"font-weight:bold; color:#8B4513\">" + render + "</table>"

        return format_html(
            render_html
        )

    cart_items.short_description = 'Products in cart'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'discount', 'total_price')
    search_fields = ('cart',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'id', 'total_price', 'date_created', 'date_shipping', 'status',
        'payment_type', 'payment_status', 'full_address')
    search_fields = ('user',)
    list_per_page = 12
    date_hierarchy = 'date_created'
    list_editable = ('status', 'date_shipping')
    list_filter = ('status', 'date_shipping', DateCommentFilter)
    readonly_fields = ('address', 'order_items',)
    fields = ('user', 'email', ('products_price', 'delivery_cost', 'total_price', 'products_amount'),
              'order_items', ('date_shipping', 'status'), ('payment_type', 'payment_status'), 'address',
              'address_last_name', ('address_street', 'address_home_number'), ('address_ZIP', 'address_city'),
              'phone_number', 'invoice')

    def address(self, instance):
        street = instance.address_street + ' ' + instance.address_home_number
        city = instance.address_ZIP + ' ' + instance.address_city
        return format_html_join(
            mark_safe('<br>'),
            '{}',
            ((line,) for line in
             [instance.address_last_name, street, city, instance.phone_number])
        )

    address.short_description = 'Full address'

    def order_items(self, instance):
        order_items = instance.order_items.all()
        shipment_items = instance.shipment.shipment_items.all()
        shipment_product = {}
        try:
            for items in shipment_items:
                shipment_product[items.product] += items.quantity
        except:
            pass
        render = '<tr><td>Title of product</td><td>Quantity</td><td>Left to ship</td><tr>'
        for line in order_items:
            render += f'<tr><td>{line.product}</td><td style="text-align:center">{line.quantity}</td>' \
                      f'<td style="text-align:center">{line.quantity - shipment_product[line.product] if line.product in shipment_product.keys() else 0}</td></tr>'
        render = "<table style=\"font-weight:bold; color:#8B4513\">" + render + "</table>"
        return format_html(
            render
        )

    order_items.short_description = 'Products in oder'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'id', 'product', 'quantity', 'price', 'discount')


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('order', 'date_created')
    readonly_fields = ('shipment_items',)
    search_fields = ('order',)
    list_per_page = 12
    date_hierarchy = 'date_created'

    def shipment_items(self, instance):
        items = instance.shipment_items.all()
        render = '<tr><td>Title of product</td><td>Quantity</td><tr>'
        for line in items:
            render += f'<tr><td>{line.product}</td><td style="text-align:center">{line.quantity}</td></tr>'
        render = "<table style=\"font-weight:bold; color:#8B4513\">" + render + "</table>"
        return format_html(
            render
        )

    shipment_items.short_description = 'Shipped products'


@admin.register(ShipmentItem)
class ShipmentItemAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'id', 'product', 'quantity',)


@admin.register(Composition)
class CompositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'counting', 'id')
