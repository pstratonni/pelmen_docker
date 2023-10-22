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

from purchaser.views import CustomAuthToken

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('purchaser.urls')),
    path('api/v1/shop/', include('shop.urls')),
    path('api/v1/token-auth/', CustomAuthToken.as_view()),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon/favicon.ico')))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
