# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.db import transaction
from django.http.response import StreamingHttpResponse
from django.shortcuts import render

from account.models import Profile, UserInfo
from competition.models import BankInfo
from business.models import BusinessAccountInfo
from utils.decorators import check_login
from utils.errors import (FileNotFound, FileTypeError, ProfileNotFound,
                          TemplateNotFound, BizAccountNotFound)
from utils.small_utils import get_now_string, get_today_string
from utils.upload_questions import upload_questions


@check_login
def index(request):
    """
    题库和比赛导航页
    :param request: 请求对象
    :return: 渲染视图和user_info用户信息数据
    """

    uid = request.GET.get('uid', '')

    try:
        profile = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        return render(request, 'err.html', ProfileNotFound)

    return render(request, 'setgames/index.html', {'user_info': profile.data})


@check_login
def set_bank(request):
    """
    配置题库页面
    :param request: 请求对象
    :return: 渲染页面返回user_info用户信息数据和bank_types题库类型数据
    """

    uid = request.GET.get('uid', '')

    try:
        profile = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        return render(request, 'err.html', ProfileNotFound)

    bank_types = []
    for i, j in BankInfo.BANK_TYPES:
        bank_types.append({'id': i, 'name': j})

    return render(request, 'setgames/bank.html', {
        'user_info': profile.data,
        'bank_types': bank_types
    })


@check_login
def template_download(request):
    """
    题库模板下载
    :param request: 请求对象
    :return: 返回excel文件的数据流
    """

    uid = request.GET.get('uid', '')

    try:
        profile = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        return render(request, 'err.html', ProfileNotFound)

    def iterator(file_name, chunk_size=512):
        with open(file_name, 'rb') as f:  # rb mode
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    template_path = 'web/static/template/template.xlsx'
    file_path = os.path.join(settings.BASE_DIR, template_path)

    if not os.path.exists(file_path):
        return render(request, 'err.html', TemplateNotFound)

    response = StreamingHttpResponse(iterator(file_path), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=template.xlsx'
    return response


@check_login
@transaction.atomic
def upload_bank(request):
    """
    上传题库
    :param request:请求对象
    :return: 返回用户信息user_info和上传成功的个数
    """

    uid = request.POST.get('uid', '')
    bank_name = request.POST.get('bank_name', '')
    bank_type = request.POST.get('bank_type')
    template = request.FILES.get('template', None)
    for k, v in dict(BankInfo.BANK_TYPES).items():
        if v == bank_type:
            bank_type = k
            break
    print(bank_type)

    if not template:
        return render(request, 'err.html', FileNotFound)

    if template.name.split('.')[-1] not in ['xls', 'xlsx']:
        return render(request, 'err.html', FileTypeError)

    try:
        profile = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        return render(request, 'err.html', ProfileNotFound)

    bank_info = BankInfo.objects.select_for_update().create(
        uid=uid,
        bank_name=bank_name or '暂无',
        bank_type=bank_type
    )

    today_bank_repo = os.path.join(settings.BANK_REPO, get_today_string())
    if not os.path.exists(today_bank_repo):
        os.mkdir(today_bank_repo)

    final_path = os.path.join(today_bank_repo, get_now_string(bank_info.bank_id)) + '.xlsx'

    with open(final_path, 'wb+') as f:
        f.write(template.read())

    choice_num, fillinblank_num = upload_questions(final_path, bank_info)

    return render(request, 'setgames/bank.html', {
        'user_info': profile.data,
        'created': {
            'choice_num': choice_num,
            'fillinblank_num': fillinblank_num
        }
    })


@check_login
def set_game(request):
    uid = request.GET.get('uid', '')

    try:
        profile = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        return render(request, 'err.html', ProfileNotFound)

    try:
        biz = BusinessAccountInfo.objects.get(email=profile.email)
    except BusinessAccountInfo.DoesNotExist:
        return render(request, 'err.html', BizAccountNotFound)

    bank_types = []
    for i, j in BankInfo.BANK_TYPES:
        bank_types.append({'id': i, 'name': j})

    form_fields = []
    for f in UserInfo._meta.fields:
        if f.name not in ['id', 'created_at', 'updated_at', 'kind_id', 'uid', 'status']:
            form_fields.append({'field_name': f.name, 'label': f.verbose_name})

    banks = BankInfo.objects.values_list('bank_name', 'bank_id', 'kind_num', 'choice_num', 'fillinblank_num').order_by('-kind_num')[:10]
    banks = [{'bank_name': b[0], 'bank_id': b[1], 'kind_num': b[2], 'total_question_num': b[3] + b[4]} for b in banks]

    return render(request, 'setgames/game.html', {
        'account_id': biz.account_id,
        'bank_types': bank_types,
        'form_fields': form_fields,
        'banks': banks,
    })
