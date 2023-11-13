import os

from djoser import email
from django.contrib.auth.tokens import default_token_generator
from djoser import utils
from djoser.conf import settings
from django.conf import settings as dj_set


class OwenAktivationEmail(email.ActivationEmail):
    template_name = 'activation.html'

    def get_context_data(self):
        # ActivationEmail can be deleted
        context = super().get_context_data()

        url_logo = os.path.join('media', 'email', 'logo_activation.jpg')
        url_bg = os.path.join('media', 'email', 'bg.png')
        url_inst = os.path.join('media', 'email', 'inst.png')
        user = context.get("user")
        context["uid"] = utils.encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = settings.ACTIVATION_URL.format(**context)
        context["user"] = user.username
        context['url_logo'] = url_logo
        context['url_bg'] = url_bg
        context['url_inst'] = url_inst
        return context
