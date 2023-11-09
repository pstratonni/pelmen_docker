import calendar
import datetime
import dateutils

from django.contrib import admin
from django.db.models import Prefetch
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.contrib.admin.sites import AdminSite
from shop_server.tasks import count_product, add_or_update_shipment_doc, add_order_to_purchaser
from icecream import ic

from shop.models import *

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
    list_display = ('colored_title', 'price', 'discount', 'active', 'date_created_format',)
    list_per_page = 12
    search_fields = ('title',)
    list_filter = ('active',)
    list_display_links = ('colored_title',)
    list_editable = ('active', 'discount', 'price')
    raw_id_fields = ('composition',)
    fields = (
        'title', 'description', 'manufacturer', 'image', ('is_price_for_one', 'weight'), ('price', 'discount'),
        'active',
        'vendor_code', ('composition', 'categories'))

    def save_model(self, request, obj, form, change):
        try:
            if form.cleaned_data['active'] != form.initial['active']:
                obj.save()
                for category in obj.categories.all().prefetch_related(
                        Prefetch('products', queryset=Product.objects.all().only('pk'))):
                    count_product.delay(category.id)
                return
        except:
            pass
        obj.save()


class CartItemInline(admin.TabularInline):
    model = CartItem
    fields = ('product', 'quantity', 'price', 'discount', 'total_price')
    readonly_fields = ('total_price',)
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'id', 'total_amount', 'total_price')
    search_fields = ('user__username__startswith',)
    readonly_fields = ('user', 'total_price', 'total_amount', 'cart_items',)
    inlines = (
        CartItemInline,
    )

    def cart_items(self, instance):
        items = instance.cart_items.all()
        render = '<tr><td>Title of product</td><td>Quantity</td><tr>'
        for line in items:
            render += f'<tr><td>{line.product}</td><td style="text-align:center">{line.quantity}</td></tr>'
        render_html = "<table style=\"font-weight:bold; color:#8B4513\">" + render + "</table>"

        return format_html(
            render_html
        )

    cart_items.short_description = 'Products in cart'

    def save_formset(self, request, form, formset, change):
        items = formset.save(commit=False)
        for item in items:
            item.update_cart_item()
        formset.save()
        Cart.objects.get(pk=int(request.POST['cart_items-0-cart'])).update_cart()

    def delete_model(self, request, obj):
        user = obj.user
        obj.delete()
        Cart.objects.create(user=user)


# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ('cart', 'product', 'quantity', 'discount', 'total_price')
#     search_fields = ('cart',)
#
#     def save_model(self, request, obj, form, change):
#         obj.update_cart_item()
#         obj.cart.update_cart()
#
#     def delete_model(self, request, obj):
#         cart = obj.cart
#         obj.delete()
#         cart.update_cart()


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'quantity', 'price', 'discount', 'total_price')
    readonly_fields = ('total_price',)
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'id', 'total_price', 'date_created', 'date_shipping', 'status',
        'payment_type', 'payment_status', 'full_address')
    search_fields = ('user__username__startswith',)
    list_per_page = 12
    list_editable = ('status', 'date_shipping')
    list_filter = ('status', 'date_shipping', DateCommentFilter)
    readonly_fields = ('address', 'order_items',)
    fields = ('user', "is_new", 'email', ('total_price', 'products_amount'),
              'order_items', ('date_shipping', 'status'), ('payment_type', 'payment_status'), 'address',
              'address_last_name', ('address_street', 'address_home_number'), ('address_ZIP', 'address_city'),
              'phone_number', 'invoice')
    inlines = (
        OrderItemInline,
    )

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
        shipment_product = {}
        try:
            shipment_items = instance.shipment.shipment_items.all()
            for items in shipment_items:
                shipment_product[items.product] += items.quantity
        except:
            pass
        render = '<tr><td>Title of product</td><td>Quantity</td><td>Left to ship</td><tr>'
        for line in order_items:
            render += f'<tr><td>{line.product}</td><td style="text-align:center">{line.quantity}</td>' \
                      f'<td style="text-align:center">{line.quantity - shipment_product[line.product] if line.product in shipment_product.keys() else line.quantity}</td></tr>'
        render = "<table style=\"font-weight:bold; color:#8B4513\">" + render + "</table>"
        return format_html(
            render
        )

    order_items.short_description = 'Products in order'

    def save_formset(self, request, form, formset, change):
        items = formset.save(commit=False)
        for item in items:
            item.update_price()
        formset.save()
        try:
            Order.objects.get(pk=int(request.POST['order_items-0-order'])).update_order()
        except:
            pass


# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('order', 'id', 'product', 'quantity', 'price', 'discount')
#
#     def save_model(self, request, obj, form, change):
#         obj.update_price()
#         obj.order.update_order()
#
#     def delete_model(self, request, obj):
#         order = obj.order
#         obj.delete()
#         order.update_order()


class ShipmentItemInline(admin.TabularInline):
    model = ShipmentItem
    fields = ('product', 'quantity')
    extra = 0


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('order', 'id', 'date_created')
    readonly_fields = ('shipment_items',)
    search_fields = ('order',)
    list_per_page = 12
    date_hierarchy = 'date_created'
    inlines = (
        ShipmentItemInline,
    )

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

    def save_formset(self, request, form, formset, change):
        formset.save()
        add_or_update_shipment_doc.delay(int(request.POST['shipment_items-0-shipment']))


# @admin.register(ShipmentItem)
# class ShipmentItemAdmin(admin.ModelAdmin):
#     list_display = ('shipment', 'id', 'product', 'quantity',)


@admin.register(Composition)
class CompositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'counting', 'id')
