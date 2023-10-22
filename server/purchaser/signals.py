from xhtml2pdf import pisa

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from purchaser.models import Purchaser
from shop.models import Cart
from shop_server import settings


@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    if created:
        Purchaser.objects.create(user=instance)
        Cart.objects.create(user=instance)
        path_pdf = settings.MEDIA_ROOT + f'/invoices/Rechnung.pdf'

        def convert_html_to_pdf(path_pdf):
            html_pdf = render_to_string('order_to_pdf.html', )
            pdf = open(path_pdf, "w+b")
            pisa_status = pisa.CreatePDF(html_pdf, dest=pdf)
            pdf.close()
            return pisa_status.error
        convert_html_to_pdf(path_pdf)

