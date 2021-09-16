# -*- coding: utf-8 -*-

from django.shortcuts import render


def home(request):
    return render(request, 'analysis/index.html', {})


def quizz(request):
    return render(request, 'analysis/quizz.html', {})