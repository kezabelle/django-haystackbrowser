# -*- coding: utf-8 -*-
try:
    from django.conf.urls import url, include
except ImportError:
    from django.conf.urls.defaults import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]
