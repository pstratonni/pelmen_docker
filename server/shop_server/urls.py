"""
URL configuration for shop_server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from .yasg import urlpatterns as swagger_url
from django.contrib.auth import views as auth_views

from purchaser.views import CustomAuthToken

urlpatterns = [
                  path(
                      "admin/password_reset/",
                      auth_views.PasswordResetView.as_view(),
                      name="admin_password_reset",
                  ),
                  path(
                      "admin/password_reset/done/",
                      auth_views.PasswordResetDoneView.as_view(),
                      name="password_reset_done",
                  ),
                  path(
                      "reset/<uidb64>/<token>/",
                      auth_views.PasswordResetConfirmView.as_view(),
                      name="password_reset_confirm",
                  ),
                  path(
                      "reset/done/",
                      auth_views.PasswordResetCompleteView.as_view(),
                      name="password_reset_complete",
                  ),
                  path('admin/', admin.site.urls),
                  path('api/v1/', include('purchaser.urls')),
                  path('api/v1/shop/', include('shop.urls.urlpatterns_shop')),
                  path('api/v1/', include('shop.urls.urlpatterns_admin')),
                  path('api/v1/token-auth/', CustomAuthToken.as_view()),
                  re_path(r'^auth/', include('djoser.urls')),
                  path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon/favicon.ico')))
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + swagger_url
