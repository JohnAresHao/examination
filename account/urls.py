# -*- coding: utf-8 -*-

from django.conf.urls import url

from account import login_render, login_views

# 登录url
urlpatterns = [
    url(r'^login_redirect$', login_views.login_redirect, name='login_redirect'),
    url(r'^signup_redirect$', login_render.signup_redirect, name='signup_redirect'),
    url(r'^email_notify$', login_render.email_notify, name='email_notify'),
    url(r'^reset_notify$', login_render.reset_notify, name='reset_notify'),
]
