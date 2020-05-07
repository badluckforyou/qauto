#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: luzhiqi
# @Email: luzhiqi@ijunhai.com
# @Date: 2020-02-09 16:34:33
# @LastEditor: luzhiqi
# @LastEditTime: 2020-04-02 16:34:33
import os
import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from autotest.document import Document
from autotest.app_settings import AppSettings




# @login_required(login_url="/login/"")表示需要登录才有权限进到这个页面
# 无权限者将被踢出到/login/界面
@login_required(login_url="/login/")
def home(request):
    """HOME界面"""
    # 获取到当前的user名, 显示在右上角
    # username = request.user.username
    username = request.session.get("user")

    # 每个新登录的测试人员, 都为其创建以其帐号命名的文件夹
    parent_folder = os.path.join(AppSettings.TESTERFOLDER, username)
    if not os.path.exists(parent_folder):
        os.mkdir(parent_folder)

    # 该文件夹下, 需要创建所有游戏对应的文件夹
    for value in AppSettings.GAMES.values():
        folder = os.path.join(parent_folder, value)
        if value and not os.path.exists(folder):
            os.mkdir(folder)

            # 每个游戏对应的文件夹下, 需要创建log, apk, steps, images 等子文件夹
            for name in ["log", "apk", "steps", "report", "images"]:
                child_folder = os.path.join(folder, name)
                if not os.path.exists(child_folder):
                    os.mkdir(child_folder)
    # manual_of_folders = [l.replace(" ", " ") for l in Document.manual_of_folders()]


    return render(request, "templates/home.html", {
                    "title": AppSettings.TITLE,
                    "company": AppSettings.COMPANY, 
                    "username": username,
                    "manual_of_folders":  Document.manual_of_folders(),
                    "common_issues": Document.common_issues(),
                    })