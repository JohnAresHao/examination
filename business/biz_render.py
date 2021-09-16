# -*- coding: utf-8 -*-

import time

from django.shortcuts import render
from django.contrib.auth.models import User

from business.models import BusinessAccountInfo
from account.models import Profile


def home(request):
    uid = request.GET.get('uid', '')

    try:
        profile = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        profile = None

    types = dict(BusinessAccountInfo.TYPE_CHOICES)

    return render(request, 'bussiness/index.html', {
        'types': types,
        'is_company_user': bool(profile) and (profile.user_src == Profile.COMPANY_USER)
    })


def notify(request):
    email = request.GET.get('email', '')
    bind = request.GET.get('bind', '')

    time.sleep(.6)

    try:
        biz = BusinessAccountInfo.objects.get(email=email)
    except BusinessAccountInfo.DoesNotExist:
        biz = None

    try:
        profile = Profile.objects.get(email=email)
    except Profile.DoesNotExist:
        profile = None

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = None

    return render(request, 'bussiness/result.html', {
        'is_registered': bool(biz) and bool(profile) and bool(user),
        'bind': bind
    })