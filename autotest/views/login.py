import sys
import logging

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout

from autotest.app_settings import AppSettings

# Create your views here.


LOGGER = logging.getLogger("autotest")

def login(request):
    if request.POST:
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember = request.POST.get("remember")
        # auth.authenticate可以自动检测输入信息在数据库中是否存在
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            request.session["user"] = username
            remember_time = 60 * 60 * 24 * 7 if remember is not None else 0
            request.session.set_expiry(remember_time)
            LOGGER.info(" %s LOGIN" % username.upper())
            return HttpResponseRedirect("/home/")
        else:
            # 失败便调用messages去打印一行数据并停留在登录界面
            messages.add_message(request, messages.WARNING, "Account or password is wrong!!!")
            return render(request, "login.html", {"title": AppSettings.TITLE})
    # 将注销的链接直接指向login，方便用户再次登录
    # 这种处理方案的弊端->即使用户不小心点开login.html，也会被清掉登录数据
    auth.logout(request)
    return render(request, "login.html", {"title": AppSettings.TITLE})