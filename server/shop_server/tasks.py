import os

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count, Q
from celery_singleton import Singleton
from django.template.loader import render_to_string
from django.core.files import File
from pathlib import Path


@shared_task(base=Singleton)
def count_product(category_id):
    from shop.models import Category
    category = Category.objects.filter(id=category_id).annotate(
        counting_base=Count('products', filter=Q(products__active=True), distinct=True)).first()
    category.counting = category.counting_base
    category.save()


@shared_task()
def send_email_with_attach(order, order_items, tax, url, err):
    html_order = render_to_string(
        'order.html',
        {
            'order': order,
            'order_items': order_items,
            'tax': tax,
        }
    )

    order_message = EmailMultiAlternatives(
        subject=f'Bestellung №{order.id} ist am {order.date_created.strftime("%d.%m.%Y")} angekommen',
        body=f'Bestellung №{order.id}',
        from_email=os.environ.get('EMAIL_USER'),
        to=[os.environ.get('EMAIL_USER'), order.email]
    )
    order_message.attach_alternative(html_order, 'text/html')

    if not err:
        path = Path(url)
        with path.open(mode='rb') as f:
            order_message.attach(f'Rechnung №{order.id}', f, 'application/pdf')
    order_message.send()
