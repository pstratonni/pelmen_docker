from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User

from shop.models import Product


class Purchaser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address_city = models.CharField(max_length=20, null=True, blank=True, verbose_name='City')
    address_ZIP = models.CharField(max_length=5, null=True, blank=True, verbose_name='ZIP')
    address_street = models.CharField(max_length=50, null=True, blank=True, verbose_name='Street')
    address_home_number = models.CharField(max_length=5, null=True, blank=True, verbose_name='Home')
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name='Phone')
    name = models.CharField(max_length=20, null=True, blank=True, verbose_name='Name', default='')
    favorite_product = models.ManyToManyField(Product, null=True, blank=True)
    sum_orders = models.DecimalField(default=0, validators=[MinValueValidator(0.0)], max_digits=8, decimal_places=2,
                                     verbose_name='Total price of all orders')
    quantity_of_orders = models.IntegerField(default=0, validators=[MinValueValidator(0.0)],
                                             )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Purchaser"
        verbose_name_plural = "Purchasers"
        ordering = ['user']
