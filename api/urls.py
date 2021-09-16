# -*- coding: utf-8 -*-

from django.conf.urls import url

from account import login_views
from competition import game_views, set_views, rank_views
from business import biz_views

# account
urlpatterns = [
    url(r'^login_normal$', login_views.normal_login, name='normal_login'),
    url(r'^login_redirect$', login_views.login_redirect, name='index'),
    url(r'^login_vcode$', login_views.login_vcode, name='login_qrcode'),
    url(r'^signup$', login_views.signup, name='signup'),
    url(r'^sendmail$', login_views.sendmail, name='sendmail'),
    url(r'^resetpasswd$', login_views.reset_password, name='reset_password'),
]

# game
urlpatterns += [
    url(r'^questions$', game_views.get_questions, name='get_questions'),
    url(r'^answer$', game_views.submit_answer, name='submit_answer'),
    url(r'^entry$', game_views.userinfo_entry, name='userinfo_entry'),
    url(r'^games/s/(\w+)$', game_views.games, name='query_games'),
]

# set
urlpatterns += [
    url(r'^banks/s/(\d+)$', set_views.banks, name='query_banks'),
    url(r'^banks/detail/(?P<bank_id>\w+)$', set_views.bank_detail, name='bank_detail'),
    url(r'^banks/set$', set_views.set_bank, name='set_bank'),
]

# rank
urlpatterns += [
    url(r'^myrank$', rank_views.get_my_rank, name='my_rank'),
]

# bussiness
urlpatterns += [
    url(r'^regbiz$', biz_views.registry_biz, name='registry biz'),
    url(r'^checkbiz$', biz_views.check_biz, name='check_biz'),
]