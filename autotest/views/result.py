import os
import json
import time
import base64
import traceback
import threading

from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from autotest.app_settings import AppSettings
from autotest.models import AutoUITestResult
from autotest.helper import _hash_encrypted, get_files
from autotest.database import DataBaseManage


database = DataBaseManage()

def get_true_username(request):
    sharer = request.GET.get("u")
    user = request.session.get("user")
    if sharer is None and user is not None:
        return user
    elif sharer is not None and sharer == user:
        return user
    else:
        return sharer


def generate_image(file, image):
    with open(file, "wb") as f:
        f.write(base64.b64decode(image))


def get_dates(query):
    dates = database.select("autotest_autouitestresult", "date", query)
    dates =  list(set([d[0] for d in dates])) if dates else []
    dates.sort()
    return ["All"] + dates


# @login_required(login_url="/login/")
def result(request):
    username = get_true_username(request)
    project = request.GET.get("project") or "All"
    date = request.GET.get("date") or "All"

    if project == "All":
        data = AutoUITestResult.objects.filter(username=username)
        result = database.select("autotest_autouitestresult", "testresult", "username='%s'" % username)
        dates = ["All"]
    elif project != "All" and date == "All":
        data = AutoUITestResult.objects.filter(Q(username=username) & Q(project=AppSettings.PROJECTS[project]))
        query = "username='%s' and project='%s'" % (username, AppSettings.PROJECTS[project])
        result = database.select("autotest_autouitestresult", "testresult", query)
        dates = get_dates(query)
    else:
        data = AutoUITestResult.objects.filter(Q(username=username) & 
                                                Q(project=AppSettings.PROJECTS[project]) &
                                                Q(date=date))
        query = "username='%s' and project='%s' and date='%s'" % (username, AppSettings.PROJECTS[project], date)
        result = database.select("autotest_autouitestresult", "testresult", query)
        query = "username='%s' and project='%s'" % (username, AppSettings.PROJECTS[project])
        dates = get_dates(query)

    if result:
        result = [r[0] for r in result]

    paginator = Paginator(data, AppSettings.ROWSNUMBER)
    page = request.GET.get("page")
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    return render(request, "templates/result.html", {
                    "title": AppSettings.TITLE,
                    "company": AppSettings.COMPANY,
                    "username": username,
                    "project": project,
                    "projects": ["All"] + list(AppSettings.PROJECTS.keys()),
                    "date": date,
                    "dates": dates,
                    "data": data,
                    "result": result})


def insert(request):
    try:
        date = request.POST.get("date")
        username = request.POST.get("username")
        project = request.POST.get("project")
        casename = request.POST.get("casename")
        runtime = request.POST.get("runtime")
        resultwanted = request.POST.get("resultwanted")
        resultinfact = request.POST.get("resultinfact")
        testresult = request.POST.get("testresult")
        costtime = request.POST.get("costtime")
        log = request.POST.get("log")
        report = request.POST.get("report")
        image = request.POST.get("image")
        filename = "%s%s.png" % (project, int(time.time()))
        filepath = os.path.join(AppSettings.TESTERFOLDER, _hash_encrypted(username), project, "images")
        file = os.path.join(filepath, filename)
        thread = threading.Thread(target=generate_image, args=(file, image))
        thread.setDaemon(False)
        thread.start()
        image = os.path.join(_hash_encrypted(username), project, "images", filename)
        AutoUITestResult.objects.create(username=username, project=project, casename=casename, date=date,
                                        runtime=runtime, resultwanted=resultwanted, resultinfact=resultinfact,
                                        testresult=testresult, costtime=costtime, log=log, report=report, image=image)
        return JsonResponse("Update test result success.", safe=False)
    except:
        traceback.print_exc()
        return JsonResponse(traceback.format_exc(), safe=False)