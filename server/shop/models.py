from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum
from django.utils.html import format_html


# from shop_server.tasks import count_product


class Manufacturer(models.Model):
    title = models.CharField(max_length=50)
    address_city = models.CharField(max_length=50)
    address_street = models.CharField(max_length=50)
    address_ZIP = models.CharField(max_length=10)
    address_home_number = models.CharField(max_length=5)
    img_manufacturer = models.ImageField(upload_to='author_img')
    activ = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

    def deactivate_manufacturer(self):
        for product in self.product_set.all():
            product.active = False
        self.save()

    class Meta:
        ordering = ['title']


class Composition(models.Model):
    title = models.CharField(max_length=150)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Category(models.Model):
    title = models.CharField(max_length=50)
    counting = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['title']


class Product(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(default='', blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True)
    is_price_for_one = models.BooleanField(default=False)
    weight = models.IntegerField(validators=[MinValueValidator(1)], default=500)
    price = models.DecimalField(validators=[MinValueValidator(0.0)], max_digits=5, decimal_places=2)
    discount = models.DecimalField(validators=[MinValueValidator(0.0)], max_digits=5, decimal_places=2,
                                   default=0)
    image = models.ImageField(upload_to='product_img')
    amount = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    composition = models.ManyToManyField(Composition, related_name='products')
    vendor_code = models.CharField(max_length=15, default='9-')
    categories = models.ManyToManyField(Category, related_name='products')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def colored_title(self):
        if not self.active:
            return format_html('<span style="color: #f00;">{}</span>',
                               self.title)
        else:
            return self.title

    colored_title.admin_order_field = 'title'

    def date_created_property(self):
        return f'{self.date_created.strftime("%d. %b. %Y")}'

    date_created_property.short_description = 'Date created'
    date_created_format = property(date_created_property)

    class Meta:
        ordering = ['id']


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders', blank=True,
                             db_index=True, )
    total_price = models.DecimalField(default=0, validators=[MinValueValidator(0.0)],
                                      max_digits=5, decimal_places=2)
    products_amount = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_shipping = models.DateField(null=True, blank=True)
    STATUSES = [
        ('UNF', 'angenommen'),
        ('CON', 'bestätigt'),
        ('COL', 'gesammelt'),
        ('SHI', 'verschickt')
    ]
    status = models.CharField(choices=STATUSES, default='UNF', max_length=3)
    PAYMENTS = [
        ('PP', 'PayPal'),
        ('BG', 'Bargeld')
    ]
    payment_type = models.CharField(choices=PAYMENTS, max_length=3, default='BG')
    PAY_STATUS = [
        ('PAI', 'bezahlt'),
        ('UNP', 'unbezahlt')
    ]
    payment_status = models.CharField(choices=PAY_STATUS, max_length=3, default='UNP')
    address_city = models.CharField(max_length=20, default='')
    address_ZIP = models.CharField(max_length=5, default='')
    address_street = models.CharField(max_length=50, default='')
    address_home_number = models.CharField(max_length=5, default='')
    address_last_name = models.CharField(max_length=20, default='')
    phone_number = models.CharField(max_length=20, default='')
    email = models.EmailField(default='')
    invoice = models.FileField(upload_to='invoices', null=True, blank=True)
    is_new = models.BooleanField(default=True)
    comment = models.TextField(max_length=250, default='', null=True)

    def __str__(self):
        return f'{self.user}, {self.date_created.strftime("%d.%m.%Y %H:%M:%S")}'

    def full_address_property(self):
        return f'{self.address_last_name}\n{self.address_street}{self.address_home_number}\n{self.address_ZIP} {self.address_city}\n{self.phone_number}'

    full_address_property.short_description = 'Full address'
    full_address = property(full_address_property)

    def update_order(self):
        x = self.order_items.aggregate(Sum('total_price'), Sum('quantity'))
        self.total_price = x['total_price__sum'] or 0
        self.products_amount = x['quantity__sum'] or 0
        self.save()

    def is_new_order(self):
        if self.is_new:
            return format_html('<span style="color: #f00;">{}</span>',
                               self.user)
        else:
            return self.user

    is_new_order.admin_order_field = 'user'

    def date_created_property(self):
        return f'{self.date_created.strftime("%d. %b. %Y %H:%M:%S")}'

    date_created_property.short_description = 'Date created'
    date_created_format = property(date_created_property)

    class Meta:
        ordering = ['-date_created']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    price = models.DecimalField(default=0, validators=[MinValueValidator(0.0)], max_digits=5, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    discount = models.DecimalField(validators=[MinValueValidator(0.0)], null=True, default=0, max_digits=5,
                                   decimal_places=2)
    total_price = models.DecimalField(default=0, validators=[MinValueValidator(0.0)], max_digits=5, decimal_places=2)

    def update_price(self):
        self.total_price = self.quantity * (self.price - self.discount)
        self.save()

    def __str__(self):
        return f'{self.order}'


class Shipment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, related_name='shipment')
    date_created = models.DateTimeField(auto_now_add=True)
    shipment_doc = models.FileField(upload_to='shipments', blank=True, null=True)

    def __str__(self):
        return f'{self.order.id}  {self.date_created.strftime("%d.%m.%Y %H:%M:%S")}'

    def date_created_property(self):
        return f'{self.date_created.strftime("%d. %b. %Y %H:%M:%S")}'

    date_created_property.short_description = 'Date created'
    date_created_format = property(date_created_property)

    def order_property(self):
        return f'{self.order.id}  {self.order}'

    order_property.short_description = 'Order'
    order_format = property(order_property)

    class Meta:
        ordering = ['order']


class ShipmentItem(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, null=True, related_name='shipment_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, related_name='shipment_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1)

    def __str__(self):
        return f'{self.shipment}'

    class Meta:
        ordering = ['id']


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='cart')
    total_price = models.DecimalField(default=0, validators=[MinValueValidator(0.0)], max_digits=5, decimal_places=2)
    total_amount = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    date_created = models.DateTimeField(auto_now_add=True)
    date_update = models.DateField(auto_now=True)

    def update_cart(self):
        x = self.cart_items.aggregate(Sum('total_price'), Sum('quantity'))
        self.total_price = x['total_price__sum'] or 0
        self.total_amount = x['quantity__sum'] or 0
        self.save()

    def __str__(self):
        return f'{self.user.username}'

    class Meta:
        ordering = ['user']


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    price = models.DecimalField(default=0, validators=[MinValueValidator(0.0)], max_digits=5, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount = models.DecimalField(validators=[MinValueValidator(0.0)], null=True, default=0, max_digits=5,
                                   decimal_places=2)
    total_price = models.DecimalField(default=0, validators=[MinValueValidator(0.0)], max_digits=5, decimal_places=2)

    def __str__(self):
        return f'{self.cart}'

    def update_cart_item(self):
        self.price = self.product.price
        self.discount = self.product.discount
        self.total_price = self.quantity * (self.price - self.discount)
        self.save()


class Tax(models.Model):
    tax = models.DecimalField(validators=[MinValueValidator(0.00), MaxValueValidator(100.00)], null=True,
                              default=7.00, max_digits=5,
                              decimal_places=2)

    def __str__(self):
        return f"{self.tax}%"

    class Meta:
        ordering = ['id']
