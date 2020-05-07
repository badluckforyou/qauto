#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: luzhiqi
# @Email: luzhiqi@ijunhai.com
# @Date: 2020-02-09 21:57:43
# @LastEditor: luzhiqi
# @LastEditTime: 2020-02-19 17:12:59

import json

from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from autotest.app_settings import AppSettings
from autotest.models import AutoTestResult



@login_required(login_url="/login/")
def result(request):
    username = request.session.get("user")

    default_game = "所有游戏"
    game = request.GET.get("game") if request.GET else default_game
    if game == default_game:
        # obder_by("") 排序; order_by("-") 反向排序
        data = AutoTestResult.objects.filter(Q(EXECUTOR=username)).order_by('RESULT')
        # web页面生成饼状图时, 需要用到所有的结果数据
        result = AutoTestResult.objects.filter(Q(EXECUTOR=username)).values("RESULT")
    else:
        data = AutoTestResult.objects.filter(Q(GAME=game) & Q(EXECUTOR=username)).order_by('RESULT')
        result = AutoTestResult.objects.filter(Q(GAME=game) & Q(EXECUTOR=username)).values("RESULT")
    
    paginator = Paginator(data, AppSettings.PHONESNUMBER)
    # paginator = Paginator(data, 1)
    page = request.GET.get("page")
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    
    # result 要转换成json的列表
    result = json.dumps([item for item in result])

    return render(request, "templates/result.html", {
                    "title": AppSettings.TITLE,
                    "company": AppSettings.COMPANY,
                    "username": username,
                    "game": game,
                    "games": AppSettings.GAMES.keys(),
                    "data": data,
                    "result": result})