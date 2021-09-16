# -*- coding: utf-8 -*-

import base64
import uuid
from io import BytesIO

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from account.models import Profile
from furl import furl
from utils.codegen import get_pic_code
from utils.errors import UserError
from utils.redis.extensions import quote, unquote
from utils.redis.rprofile import (get_vcode, set_profile, set_signcode,
                                  set_vcode, set_passwd, set_has_sentemail, get_has_sentemail,
                                  set_has_sentregemail, get_has_sentregemail)
from utils.response import json_response
from utils.wechat_utils import AUTHORIZE_URI, get_access_info, get_userinfo


def quote_state(state):
    return quote(state)


def unquote_state(request, state):
    if state == 'wxweblogin':
        return settings.WEB_INDEX_URI
    return unquote(state, buf=True) or ''


@transaction.atomic
def login_redirect(request):
    """
    微信登录重定向
    :param request: 请求对象
    :return: 获取用户信息并跳转回redirect_uri
    """

    code = request.GET.get('code', '')
    state = request.GET.get('state', '')

    state = unquote_state(request, state)

    access_info = get_access_info(settings.WXWEB_LOGIN_PARAMS.get('appid', 'wxea43537839d347b1'), settings.WXWEB_LOGIN_PARAMS.get('appsecret', '02d0bdd56281a583b7d8a83f7379247e'), code)
    if 'errcode' in access_info:
        return redirect(AUTHORIZE_URI.format(settings.WXWEB_LOGIN_PARAMS.get('appid'), settings.WEB_LOGIN_REDIRECT_URI, 'snsapi_userinfo', state))

    userinfo = get_userinfo(access_info.get('access_token', ''), access_info.get('openid', ''))
    if 'openid' not in userinfo:
        return redirect(AUTHORIZE_URI.format(settings.WXWEB_LOGIN_PARAMS.get('appid'), settings.WEB_LOGIN_REDIRECT_URI, 'snsapi_userinfo', state))

    profile_values = {
        'openid': userinfo.get('openid', ''),
        'user_src': 1,
        'sex': userinfo.get('sex', 0),
        'nickname': userinfo.get('nickname', ''),
        'avatar': userinfo.get('headimgurl', ''),
        'country': userinfo.get('country', ''),
        'province': userinfo.get('province', ''),
        'city': userinfo.get('city', ''),
    }

    profile, created = Profile.objects.select_for_update().get_or_create(openid=userinfo.get('openid', ''), defaults=profile_values)
    if not profile.unionid:
        profile.unionid = userinfo.get('unionid', '')
        profile.save()

    if not created:
        for key, value in profile_values.items():
            setattr(profile, key, value)
        profile.save()

    set_profile(profile.data)

    request.session['uid'] = profile.uid
    request.session['username'] = profile.name

    return redirect(furl(state).url)


@csrf_exempt
@transaction.atomic
def normal_login(request):
    """
    普通登录视图
    :param request: 请求对象
    :return: 返回json数据: user_info: 用户信息;has_login: 用户是否已登录
    """

    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    sign = request.POST.get('sign', '')
    vcode = request.POST.get('vcode', '')

    result = get_vcode(sign)
    if not (result and (result.decode('utf-8') == vcode.lower())):
        return json_response(*UserError.VeriCodeError)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return json_response(*UserError.UserNotFound)

    user = authenticate(request, username=user.username, password=password)

    if user is not None:
        login(request, user)
        profile, created = Profile.objects.select_for_update().get_or_create(
            email=user.email,
        )
        if profile.user_src != Profile.COMPANY_USER:
            profile.name = user.username
            profile.user_src = Profile.NORMAL_USER
            profile.save()
        request.session['uid'] = profile.uid
        request.session['username'] = profile.name
        set_profile(profile.data)
    else:
        return json_response(*UserError.PasswordError)

    return json_response(200, 'OK', {
        'user_info': profile.data,
        'has_login': bool(profile),
    })


def login_vcode(request):
    """
    登录验证码获取
    :param request: 请求对象
    :return: vcode: 验证码图片的base64编码; sign: 校验码
    """

    b = BytesIO()
    img, check = get_pic_code()
    img.save(b, format='png')

    vcode = base64.b64encode(b.getvalue())

    sign = str(uuid.uuid1())
    set_vcode(sign, ''.join([str(i) for i in check]).lower())

    return json_response(200, 'OK', {
        'vcode': vcode.decode('utf-8'),
        'sign': sign
    })


@csrf_exempt
@transaction.atomic
def signup(request):
    """
    用户注册接口
    :param request: 请求对象
    :return: 返回email用户注册邮箱和校验码sign
    """

    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    password_again = request.POST.get('password_again', '')
    vcode = request.POST.get('vcode', '')
    sign = request.POST.get('sign')

    if password != password_again:
        return json_response(*UserError.PasswordError)

    result = get_vcode(sign)
    if not (result and (result.decode('utf-8') == vcode.lower())):
        return json_response(*UserError.VeriCodeError)

    if User.objects.filter(email__exact=email).exists():
        return json_response(*UserError.UserHasExists)

    username = email.split('@')[0]
    if User.objects.filter(username__exact=username).exists():
        username = email

    User.objects.create_user(
        is_active=False,
        is_staff=False,
        username=username,
        email=email,
        password=password,
    )

    Profile.objects.create(
        name=username,
        email=email
    )

    sign = str(uuid.uuid1())
    set_signcode(sign, email)

    return json_response(200, 'OK', {
        'email': email,
        'sign': sign
    })


def sendmail(request):
    to_email = request.GET.get('email', '')
    sign = request.GET.get('sign', '')

    if not get_has_sentregemail(to_email):
        title = '[Quizz.cn用户激活邮件]'
        sender = settings.EMAIL_HOST_USER
        url = settings.DOMAIN + '/auth/email_notify?email=' + to_email + '&sign=' + sign
        msg = '您好，Quizz.cn管理员想邀请您激活您的用户，点击链接激活。{}'.format(url)

        ret = send_mail(title, msg, sender, [to_email], fail_silently=True)
        if not ret:
            return json_response(*UserError.UserSendEmailFailed)

        set_has_sentregemail(to_email)

        return json_response(200, 'OK', {})
    else:
        return json_response(*UserError.UserHasSentEmail)


@csrf_exempt
@transaction.atomic
def reset_password(request):
    email = request.POST.get('email', '')
    new_password = request.POST.get('new_password', '')
    new_password_again = request.POST.get('new_password_again', '')
    is_biz = request.POST.get('is_biz', 0)

    if new_password != new_password_again:
        return json_response(*UserError.PasswordError)

    try:
        User.objects.get(email=email)
    except User.DoesNotExist:
        return json_response(*UserError.UserNotFound)

    if not get_has_sentemail(email):
        sign = str(uuid.uuid1())
        set_passwd(sign, new_password)
        set_has_sentemail(email)

        title = '[Quizz.cn密码重置邮件]'
        sender = settings.EMAIL_HOST_USER
        url = settings.DOMAIN + '/auth/reset_notify?email=' + email + '&sign=' + sign + '&is_biz=' + str(is_biz)
        msg = '您好，Quizz.cn管理员想邀请您确认是否重置密码？{}'.format(url)

        ret = send_mail(title, msg, sender, [email], fail_silently=True)
        if not ret:
            return json_response(*UserError.UserSendEmailFailed)

        return json_response(200, 'OK', {})

    else:
        return json_response(*UserError.UserHasSentEmail)
