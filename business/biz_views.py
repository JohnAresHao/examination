# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

from account.models import Profile
from business.models import BusinessAccountInfo

from utils.response import json_response
from utils.errors import BizError, UserError


def check_biz(request):
    email = request.GET.get('email', '')

    try:
        biz = BusinessAccountInfo.objects.get(email=email)
    except BusinessAccountInfo.DoesNotExist:
        biz = None

    return json_response(200, 'OK', {
        'userexists': User.objects.filter(email=email).exists(),
        'bizaccountexists': bool(biz)
    })


@csrf_exempt
@transaction.atomic
def registry_biz(request):
    email = request.POST.get('email', '')
    name = request.POST.get('name', '')
    username = request.POST.get('username', '')
    phone = request.POST.get('phone', '')
    ctype = request.POST.get('type', BusinessAccountInfo.INTERNET)
    flag = int(request.POST.get('flag', 2))

    uname = email.split('@')[0]
    if not User.objects.filter(username__exact=name).exists():
        final_name = username
    elif not User.objects.filter(username__exact=uname).exists():
        final_name = uname
    else:
        final_name = email

    if flag == 2:
        user = User.objects.create_user(
            username=final_name,
            email=email,
            password=settings.INIT_PASSWORD,
            is_active=False,
            is_staff=False
        )
    if flag == 1:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return json_response(*UserError.UserNotFound)

    pvalues = {
        'phone': phone,
        'name': final_name,
        'user_src': Profile.COMPANY_USER,
    }

    profile, _ = Profile.objects.select_for_update().get_or_create(email=email)

    for k, v in pvalues.items():
        setattr(profile, k, v)
    profile.save()

    bizvalues = {
        'company_name': name,
        'company_username': username,
        'company_phone': phone,
        'company_type': ctype,
    }

    biz, _ = BusinessAccountInfo.objects.select_for_update().get_or_create(
        email=email,
        defaults=bizvalues
    )

    return json_response(200, 'OK', {
        'name': final_name,
        'email': email,
        'flag': flag
    })