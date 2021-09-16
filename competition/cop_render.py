# -*- coding: utf-8 -*-

import collections
import json

from django.shortcuts import render

from account.models import Profile
from competition.models import BankInfo, CompetitionKindInfo, CompetitionQAInfo
from utils.decorators import check_copstatus, check_login
from utils.errors import (BankInfoNotFound, CompetitionNotFound,
                          ProfileNotFound, QuestionLogNotFound,
                          QuestionNotSufficient)
from utils.redis.rpageconfig import get_pageconfig, get_form_regex
from utils.redis.rprofile import get_enter_userinfo
from utils.redis.rrank import get_rank, get_rank_data


# @check_login
def home(request):
    """
    比赛首页首页视图
    :param request: 请求对象
    :return: 渲染视图: user_info: 用户信息; kind_info: 比赛信息;is_show_userinfo: 是否展示用户信息表单;user_info_has_entered: 是否已经录入表单;
             userinfo_fields: 表单字段;option_fields: 表单字段中呈现为下拉框的字段;
    """

    uid = request.GET.get('uid', '')
    kind_id = request.GET.get('kind_id', '')
    created = request.GET.get('created', '0')

    try:
        kind_info = CompetitionKindInfo.objects.get(kind_id=kind_id)
    except CompetitionKindInfo.DoesNotExist:
        return render(request, 'err.html', CompetitionNotFound)

    try:
        bank_info = BankInfo.objects.get(bank_id=kind_info.bank_id)
    except BankInfo.DoesNotExist:
        return render(request, 'err.html', BankInfoNotFound)

    try:
        profile = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        return render(request, 'err.html', ProfileNotFound)

    if kind_info.question_num > bank_info.total_question_num:
        return render(request, 'err.html', QuestionNotSufficient)

    show_info = get_pageconfig(kind_info.app_id).get('show_info', {})
    is_show_userinfo = show_info.get('is_show_userinfo', False)
    form_fields = collections.OrderedDict()
    form_regexes = []

    if is_show_userinfo:
        userinfo_fields = show_info.get('userinfo_fields', '').split('#')
        for i in userinfo_fields:
            form_regexes.append(get_form_regex(i))
        userinfo_field_names = show_info.get('userinfo_field_names', '').split('#')
        for i in range(len(userinfo_fields)):
            form_fields.update({userinfo_fields[i]: userinfo_field_names[i]})

    return render(request, 'competition/index.html', {
        'user_info': profile.data,
        'kind_info': kind_info.data,
        'bank_info': bank_info.data,
        'is_show_userinfo': 'true' if is_show_userinfo else 'false',
        'userinfo_has_enterd': 'true' if get_enter_userinfo(kind_id, uid) else 'false',
        'userinfo_fields': json.dumps(form_fields) if form_fields else '{}',
        'option_fields': json.dumps(show_info.get('option_fields', '')),
        'field_regexes': form_regexes,
        'created': created
    })


@check_login
@check_copstatus
def game(request):
    """
    返回比赛题目信息的视图
    :param request: 请求对象
    :return: 渲染视图: user_info: 用户信息;kind_id: 比赛唯一标识;kind_name: 比赛名称;cop_finishat: 比赛结束时间;rule_text: 大赛规则;
    """

    uid = request.GET.get('uid', '')
    kind_id = request.GET.get('kind_id', '')

    try:
        kind_info = CompetitionKindInfo.objects.get(kind_id=kind_id)
    except CompetitionKindInfo.DoesNotExist:
        return render(request, 'err.html', CompetitionNotFound)

    try:
        bank_info = BankInfo.objects.get(bank_id=kind_info.bank_id)
    except BankInfo.DoesNotExist:
        return render(request, 'err.html', BankInfoNotFound)

    try:
        profile = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        return render(request, 'err.html', ProfileNotFound)

    if kind_info.question_num > bank_info.total_question_num:
        return render(request, 'err.html', QuestionNotSufficient)

    pageconfig = get_pageconfig(kind_info.app_id)

    return render(request, 'competition/game.html', {
        'user_info': profile.data,
        'kind_id': kind_info.kind_id,
        'kind_name': kind_info.kind_name,
        'cop_finishat': kind_info.cop_finishat,
        'period_time': kind_info.period_time,
        'rule_text': pageconfig.get('text_info', {}).get('rule_text', '')
    })


@check_login
def result(request):
    """
    比赛结果和排行榜的视图
    :param request: 请求对象
    :return: 渲染视图: qa_info: 答题记录数据;user_info: 用户信息数据;kind_info: 比赛信息数据;rank: 该用户当前比赛排名
    """

    uid = request.GET.get('uid', '')
    kind_id = request.GET.get('kind_id', '')
    qa_id = request.GET.get('qa_id', '')

    try:
        profile = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        return render(request, 'err.html', ProfileNotFound)

    try:
        kind_info = CompetitionKindInfo.objects.get(kind_id=kind_id)
    except CompetitionKindInfo.DoesNotExist:
        return render(request, 'err.html', CompetitionNotFound)

    try:
        qa_info = CompetitionQAInfo.objects.get(qa_id=qa_id, uid=uid)
    except CompetitionQAInfo.DoesNotExist:
        return render(request, 'err.html', QuestionLogNotFound)

    return render(request, 'competition/result.html', {
        'qa_info': qa_info.detail,
        'user_info': profile.data,
        'kind_info': kind_info.data,
        'rank': get_rank(kind_id, uid)
    })


@check_login
def rank(request):
    """
    排行榜数据视图
    :param request: 请求对象
    :return: 渲染视图: user_info: 用户信息;kind_info: 比赛信息; rank: 所有比赛排名;
    """

    uid = request.GET.get('uid', '')
    kind_id = request.GET.get('kind_id', '')

    try:
        profile = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        return render(request, 'err.html', ProfileNotFound)

    try:
        kind_info = CompetitionKindInfo.objects.get(kind_id=kind_id)
    except CompetitionKindInfo.DoesNotExist:
        return render(request, 'err.html', CompetitionNotFound)

    ranks, rank_data = get_rank_data(kind_id)
    for i in range(len(rank_data)):
        rank_data[i].update({'rank': i + 1})
        rank_data[i]['time'] = rank_data[i]['time'] / 1000.000

    return render(request, 'competition/rank.html', {
        'user_info': profile.data,
        'kind_info': kind_info.data,
        'rank': rank_data
    })


@check_login
def search(request):
    """
    搜索查询视图
    :param request: 请求对象
    :return: 渲染视图: user_info: 用户信息;result:查询结果比赛信息集合;key: 查询结果的关键字,是根据比赛名称查询还是根据赞助商关键字查询的结果
    """

    uid = request.GET.get('uid', '')
    keyword = request.GET.get('keyword', '')

    try:
        profile = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        render(request, 'err.html', ProfileNotFound)

    keyword = keyword.strip(' ')

    kinds = CompetitionKindInfo.objects.filter(kind_name__contains=keyword)
    key = 'kind'

    if not kinds:
        kinds = CompetitionKindInfo.objects.filter(sponsor_name__contains=keyword)
        key = 'sponsor'

    return render(request, 'competition/search.html', {
        'result': kinds,
        'key': key or ''
    })


@check_login
def contact(request):
    """
    联系我们视图
    :param request: 请求对象
    :return: 渲染视图: user_info: 用户信息
    """

    uid = request.GET.get('uid', '')
    try:
        profile = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        return render(request, 'err.html', ProfileNotFound)

    return render(request, 'web/contact_us.html', {'user_info': profile.data})


def donate(request):
    """
        捐助视图
        :param request: 请求对象
        :return: 渲染视图: user_info: 用户信息
    """

    uid = request.GET.get('uid', '')
    try:
        profile = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        profile = None

    return render(request, 'web/donate.html', {'user_info': profile.data if profile else None})
