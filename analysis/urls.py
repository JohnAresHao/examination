# -*- coding: utf-8 -*-

from django.conf.urls import url

from analysis import analysis_render


urlpatterns = [
    url('^$', analysis_render.home, name='home'),
    url(r'^quizz$', analysis_render.quizz, name='quizz'),
]