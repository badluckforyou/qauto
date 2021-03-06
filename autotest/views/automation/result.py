import os
import json
import time
import base64
import traceback
import threading

from django.db.models import Q, Count
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from autotest.app_settings import AppSettings
from autotest.models import AutoUITestResult, Task
from autotest.helper import _hash_encrypted, get_files
from autotest.query import select_uitestresult



def get_true_username(request):
    sharer = request.GET.get("u")
    user = request.session.get("user")
    if sharer is None and user is not None:
        return user
    elif sharer is not None and sharer == user:
        return user
    else:
        return sharer


def generate_images(files, images):
    if isinstance(files, list):
        for i, v in enumerate(files):
            v = os.path.join(AppSettings.TESTERFOLDER, v)
            with open(v, "wb") as f:
                f.write(base64.b64decode(images[i]))
    else:
        files = os.path.join(AppSettings.TESTERFOLDER, files)
        with open(files, "wb") as f:
            f.write(base64.b64decode(images))


def get_dates(condition):
    date_query = {"wants": "date", "condition": condition}
    dates = select_uitestresult(**date_query)
    dates =  list(set([d[0] for d in dates])) if dates else []
    dates.sort()
    return ["All"] + dates


# @login_required(login_url="/login/")
def result(request):
    username = get_true_username(request)
    project = request.GET.get("project") or "All"
    date = request.GET.get("date") or "All"
    tasks = data = []
    success = failure = {"testresult__count": 0}
    if project == "All":
        tasks = Task.objects.filter(Q(username=username) & Q(status__in=["完成", "执行"]))
    elif project != "All" and date == "All":
        tasks = Task.objects.filter(Q(username=username) & Q(project=project) & Q(status__in=["完成", "执行"]))
    else:
        data = AutoUITestResult.objects.filter(Q(username=username) & Q(date=date) &
                                                    Q(project=AppSettings.PROJECTS[project]))
        success = AutoUITestResult.objects.filter(Q(username=username) & Q(date=date) & Q(testresult="通过") &
                                                    Q(project=AppSettings.PROJECTS[project])).aggregate(Count("testresult"))
        failure = AutoUITestResult.objects.filter(Q(username=username) & Q(date=date) & Q(testresult="失败") &
                                                    Q(project=AppSettings.PROJECTS[project])).aggregate(Count("testresult"))
        
    paginator = Paginator(data, AppSettings.ROWSNUMBER)
    page = request.GET.get("page")
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    return render(request, "templates/automation/result.html", {
                    "title": AppSettings.TITLE,
                    "company": AppSettings.COMPANY,
                    "username": username,
                    "project": project,
                    "projects": list(AppSettings.PROJECTS.keys()),
                    "date": date,
                    "tasks": tasks or None,
                    "data": data or None,
                    "success": success["testresult__count"],
                    "failure": failure["testresult__count"],})


def insert(request):
    """
    Sub-server 在每条用例执行完后会将结果传送过来, 数据包含以下
        date: 整个自动化测试执行的时间, 用以在result.html上进行自动化测试结果的拆分
        username: 执行测试人员的名称, str
        project: 测试用例所属的项目, str
        casename: 测试用例的名称, str
        runtime: 测试用例执行的时间, str
        resultwanted: 测试用例中的期望结果, str
        resultinfact: 测试的实际结果, str
        testresult: 测试用例的结果, str
        costtime: 测试用例执行耗时, str
        log: 测试用例执行时生成的log日志, str
        report: 测试用例的详细信息, str
        images: 测试中产生的截图, list
    """
    try:
        username = request.POST.get("username")
        project = request.POST.get("project")
        images = request.POST.get("image")
        filepath = os.path.join(_hash_encrypted(username), project, "images")
        if isinstance(images, list):
            files = []
            for image in images:
                filename = "%s.png" % int(time.time() * 100000)
                files.append(os.path.join(filepath, filename))
        else:
            filename = "%s.png" % int(time.time() * 100000)
            files = os.path.join(filepath, filename)
        thread = threading.Thread(target=generate_images, args=(files, images))
        thread.setDaemon(False)
        thread.start()
        data = {
            "username": username,
            "project": project,
            "casename": request.POST.get("casename"),
            "runtime": request.POST.get("runtime"),
            "resultwanted": request.POST.get("resultwanted"),
            "resultinfact": request.POST.get("resultinfact"),
            "testresult": request.POST.get("testresult"),
            "costtime": request.POST.get("costtime"),
            "report": request.POST.get("report"),
            "date": request.POST.get("date"),
            "log": request.POST.get("log"),
            "image": ",".join(files) if isinstance(files, list) else files
        }
        image = os.path.join(_hash_encrypted(username), project, "images", filename)
        AutoUITestResult.objects.create(**data)
        return JsonResponse("Update test result success.", safe=False)
    except:
        traceback.print_exc()
        return JsonResponse(traceback.format_exc(), safe=False)