# -*- coding: utf-8 -*-

from django.conf.urls import url

from business import biz_render


urlpatterns = [
    url(r'^$', biz_render.home, name='index'),
    url(r'^notify$', biz_render.notify, name='notify'),
]