import re
import os
import ujson as json
import requests

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from autotest.helper import _hash_encrypted as _
from autotest.app_settings import AppSettings


def get_csdn_data():
    data = []
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
    try:
        response = requests.get("https://www.csdn.net/", headers=headers)
    except:
        return
    if response.status_code == 200:
        csdn_html = "".join(response.text.splitlines())
        main = re.findall(r"<main>.*?</main>", csdn_html)
        if not main:
            return
        essay = re.findall(r"<h2>.*?</h2>", main[0])
        if not essay:
            return
        for e in essay:
            d = {}
            fuzzy_title = re.findall(r"&request_id='.*?</a>", e)
            if not fuzzy_title:
                continue
            exact_title = re.findall(r">.*?<", fuzzy_title[0])
            if not exact_title:
                continue
            title = exact_title[-1].replace(">", "").replace("<", "").replace(" ", "")
            url = re.findall(r'[a-zA-z]+://[^\s]*"', e)
            if not url:
                continue
            d.setdefault("title", title)
            d.setdefault("url", url[0].replace('"', ""))
            data.append(d)
    return data


def get_testerhome_data():
    data = []
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
    try:
        response = requests.get("https://testerhome.com/topics/excellent", headers=headers)
    except:
        return
    if response.status_code == 200:
        testerhome_html = "".join(response.text.splitlines())
        main = re.findall(r'<div class="panel-body item-list">.*?<div class="panel-footer clearfix">', testerhome_html)
        if not main:
            return
        essay = re.findall(r"<a title=.*?</a>", main[0])
        pattern = re.compile(r"<a title=.*?<span")
        for e in essay:
            d = {}
            if not pattern.match(e):
                continue
            e = pattern.findall(e)[0]
            fuzzy_title = re.findall(r"=.*? href=", e)
            if not fuzzy_title:
                continue
            exact_title = re.findall(r'".*?"', fuzzy_title[0])
            if not exact_title:
                continue
            title = "".join(exact_title[0])
            url = re.findall(r'/[^\s]*/\d+', e)
            if not url:
                continue
            d.setdefault("title", title.replace('"', ""))
            d.setdefault("url", "https://testerhome.com%s" % url[0])
            data.append(d)
    return data


# @login_required(login_url="/login/")表示需要登录才有权限进到这个页面
# 无权限者将被踢出到/login/界面
@login_required(login_url="/login/")
def home(request):
    """HOME界面"""
    # 获取到当前的user名, 显示在右上角
    # username = request.user.username
    username = request.session.get("user")

    # 每个新登录的测试人员, 都为其创建以其帐号命名的文件夹
    parent_folder = os.path.join(AppSettings.TESTERFOLDER, _(username))
    if not os.path.exists(parent_folder):
        os.mkdir(parent_folder)

    # 该文件夹下, 需要创建所有游戏对应的文件夹
    for value in AppSettings.PROJECTS.values():
        folder = os.path.join(parent_folder, value)
        if value and not os.path.exists(folder):
            os.mkdir(folder)
        child_folder = os.path.join(folder, "images")
        if value and not os.path.exists(child_folder):
            os.mkdir(child_folder)
    return render(request, "templates/home.html", {
                    "username": username,
                    "title": AppSettings.TITLE,
                    "company": AppSettings.COMPANY, 
                    "csdn": get_csdn_data() or None,
                    "testerhome": get_testerhome_data() or None,
                    })