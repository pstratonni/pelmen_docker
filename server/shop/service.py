import base64
import os
from pathlib import Path


from decouple import config
from django.conf import settings

from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django_filters import rest_framework as filters
from xhtml2pdf import pisa

from shop.models import Product



class ChartFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class ProductFilter(filters.FilterSet):
    category = ChartFilterInFilter(field_name='category', lookup_expr='in')

    class Meta:
        model = Product
        fields = ['category']


def get_img_file_as_base64():
    url = os.path.join(settings.BASE_DIR, 'media', 'author_img', 'pdf_logo.jpg')
    with open(url, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode()


def create_pdf(order, order_items, tax, ):
    img = get_img_file_as_base64()
    html_pdf = render_to_string(
        'order_to_pdf.html',
        {
            'order': order,
            'order_items': order_items,
            'tax': tax,
            'img': img
        })
    url = os.path.join(settings.BASE_DIR, 'media', 'author_img', f'Invoice №{order.id}.pdf')
    pdf = open(url, "w+b")
    pisa_status = pisa.CreatePDF(html_pdf, dest=pdf)
    pdf.close()
    if not pisa_status.err:
        path = Path(url)
        with path.open(mode='rb') as f:
            order.invoice = File(f, name=path.name)
            order.save()

    return url, pisa_status.err


