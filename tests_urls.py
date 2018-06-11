# -*- coding: utf-8 -*-
try:
    from django.conf.urls import url, include
except ImportError:
    from django.conf.urls.defaults import url, include
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured

try:
    urlpatterns = [
        url(r'^admin/', include(admin.site.urls)),
    ]
except ImproperlyConfigured:  # >= Django 2.0
    urlpatterns = [
        url(r'^admin/', admin.site.urls),
    ]
