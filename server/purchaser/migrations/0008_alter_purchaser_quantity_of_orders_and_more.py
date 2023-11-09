# Generated by Django 4.2.6 on 2023-11-06 20:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchaser', '0007_alter_purchaser_quantity_of_orders'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaser',
            name='quantity_of_orders',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='purchaser',
            name='sum_orders',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Total price of all orders'),
        ),
    ]
