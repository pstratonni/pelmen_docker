import os

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count, Q, Sum
from celery_singleton import Singleton
from django.template.loader import render_to_string
from pathlib import Path
from django.core.files import File
from icecream import ic

from xhtml2pdf import pisa


@shared_task(base=Singleton)
def count_product(category_id: int):
    from shop.models import Category
    category = Category.objects.filter(id=category_id).annotate(
        counting_base=Count('products', filter=Q(products__active=True), distinct=True)).first()
    category.counting = category.counting_base
    category.save()


@shared_task()
def send_email_with_attach(order_id):
    from shop.models import Order, Tax, OrderItem
    order = Order.objects.get(pk=order_id)
    order_items = OrderItem.objects.filter(order=order)
    tax_persent = Tax.objects.all().latest('id')
    tax_sum = float(tax_persent.tax / 100 * order.total_price * 100 // 1 / 100)
    tax = {
        'tax_cost': tax_persent.tax,
        'tax_sum': tax_sum,
    }
    img_url = os.path.join(settings.BASE_DIR, 'media/author_img', 'pdf_logo.jpg')
    html_pdf = render_to_string(
        'order_to_pdf.html',
        {
            'order': order,
            'order_items': order_items,
            'tax': tax,
            'url': img_url
        })
    url = os.path.join(settings.BASE_DIR, 'media', 'invoices', f'Invoice №{order.id}.pdf')
    pdf = open(url, "w+b")
    pisa_status = pisa.CreatePDF(html_pdf, dest=pdf)
    pdf.close()

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
    order_message.attach_file(url)
    order_message.send()
    if not pisa_status.err:
        path = Path(url)
        with path.open(mode='rb') as f:
            order.invoice = File(f, name=path.name)
            order.save()
    os.remove(url)


@shared_task()
def add_order_to_purchaser(user):
    from purchaser.models import Purchaser
    purchaser = Purchaser.objects.filter(user=user).prefetch_related('favorite_product').annotate(
        sum_orders_base=Sum('user__orders__total_price'),
        quantity_of_orders_base=Count('user__orders')).first()
    purchaser.sum_orders = purchaser.sum_orders_base
    purchaser.quantity_of_orders = purchaser.quantity_of_orders_base
    purchaser.save()


@shared_task()
def add_or_update_shipment_doc(shipment_id: int):
    from shop.models import Shipment
    shipment = Shipment.objects.get(pk=shipment_id).prefetch_related('shipment_items')
    img_url = os.path.join(settings.BASE_DIR, 'media/author_img', 'pdf_logo.jpg')
    html_shipment_to_pdf = render_to_string(
        'shipment_to_pdf.html',
        {
            'order': shipment,
            'order_items': shipment.shipment_items,
            'url': img_url,
        }
    )
    url = os.path.join(settings.BASE_DIR, 'media', 'invoices',
                       f'Liferschein №{shipment.id} to Invoice №{shipment.order.id}.pdf')
    pdf = open(url, "w+b")
    pisa_status = pisa.CreatePDF(html_shipment_to_pdf, dest=pdf)
    pdf.close()
    if not pisa_status.err:
        path = Path(url)
        with path.open(mode='rb') as f:
            shipment.shipment_doc = File(f, name=path.name)
            shipment.save()
    os.remove(url)
