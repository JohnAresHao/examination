# -*- coding: utf-8 -*-

from django.conf.urls import include, url

from competition import cop_render, set_render

# 比赛url
urlpatterns = [
    url(r'^$', cop_render.home, name='index'),
    url(r'^game$', cop_render.game, name='game'),
    url(r'^result$', cop_render.result, name='result'),
    url(r'^rank$', cop_render.rank, name='rank'),
    url(r'^search$', cop_render.search, name='search'),
    url(r'^contact$', cop_render.contact, name='contact'),
    url(r'^donate$', cop_render.donate, name='donate'),
]

# 配置比赛url
urlpatterns += [
    url(r'^set$', set_render.index, name='set_index'),
    url(r'^set/bank$', set_render.set_bank, name='set_bank'),
    url(r'^set/bank/tdownload$', set_render.template_download, name='template_download'),
    url(r'^set/bank/upbank$', set_render.upload_bank, name='upload_bank'),
    url(r'^set/game$', set_render.set_game, name='set_game'),
]
