#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: luzhiqi
# @Email: luzhiqi@ijunhai.com
# @Date: 2020-02-09 16:33:27
# @LastEditor: luzhiqi
# @LastEditTime: 2020-02-09 16:33:27

from django.shortcuts import render

from autotest.app_settings import AppSettings

def page_not_found(request, exception):
    '''404页面'''
    return render(request, 'templates/404.html', {'title': AppSettings.TITLE})