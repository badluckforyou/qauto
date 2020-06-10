import os
import sys
import time
import ujson as json
import socket
import hashlib
import logging
import asyncio
import requests
import threading
import traceback

from contextlib import suppress

from django.db.models import Q
from django.contrib import auth
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from autotest.app_settings import AppSettings
from autotest.helper import _hash_encrypted, get_specified_files
from autotest.models import SubServer, Task
from autotest.database import dbmanage
from autotest.task_watching import watching



LOGGER = logging.getLogger("autotest")
# 任务池监控django运行时直接执行
watching_thread = threading.Thread(target=watching, args=())
watching_thread.setDaemon(False)
watching_thread.start()



def _remove_file(filepath, key):
    for file in os.listdir(filepath):
        if file.endswith(key):
            os.remove(os.path.join(filepath, file))


def remove_file(filepath, key):
    """根据key来删除文件"""
    if isinstance(key, list):
        [_remove_file(filepath, item) for item in key]
    elif isinstance(key, str):
        _remove_file(filepath, key)
    else:
        raise("WRONG KEY OF REMOVING FILES!!!")


def get_sub_servers(username):
    """从数据库中获取sub-server列表"""
    sub_servers = list()
    _sub_servers = dbmanage.select("autotest_subserver", "username, server", "single=0 and status=0")
    if _sub_servers:
        sub_servers = [' - '.join(s) for s in _sub_servers]
    my_sub_server = dbmanage.select("autotest_subserver", "username, server", "username='%s' and single=1 and status=0" % username)
    if my_sub_server:
        sub_servers += [' - '.join(m) for m in my_sub_server]
    return sub_servers


def get_status(request):
    status = request.GET.get("s")
    try:
        status = int(status)
    except:
        status = 0
    return status


@login_required(login_url="/login/")
def automated_testing(request):
    """执行自动化测试界面"""
    username = request.session.get("user")
    project = request.GET.get("project")
    if project is None:
        for k in AppSettings.PROJECTS.keys():
            project = k
            break
    packages = AppSettings.PACKAGES[project]
    platform = "ios"
    message = None
    if request.POST:
        message = upload_file(request)

    filepath = os.path.join(AppSettings.TESTERFOLDER, _hash_encrypted(username), AppSettings.PROJECTS[project])
    testfiles = list(get_specified_files(filepath, ".csv"))
    testfiles.sort()

    sub_servers = get_sub_servers(username)

    status = get_status(request)
    if status == 0:
        tasks = Task.objects.filter(Q(username=username) & Q(show=0)).order_by("status")
    elif status == 1:
        tasks = Task.objects.filter(Q(username=username) & Q(show=0)).order_by("-status")
    tasks_num = len(tasks)

    if request.GET.get("n") is None:
        show_num = 3
    else:
        show_num = sum([int(i) for i in request.GET.get("n").split(" ")])
    if show_num > tasks_num:
        show_num = tasks_num
    tasks = tasks[:show_num]

    total_tasks = Task.objects.filter(Q(status="队列") | Q(status="执行") & Q(show=0))
    total_tasks_num = len(total_tasks)

    return render(request, "templates/automation.html", {
                    "title": AppSettings.TITLE,
                    "company": AppSettings.COMPANY,
                    "username": username,
                    "project": project,
                    "packages": packages,
                    "platform": platform,
                    "message": message,
                    "projects": AppSettings.PROJECTS.keys(),
                    "platforms": AppSettings.PLATFORMS,
                    "files": testfiles,
                    "subservers": sub_servers,
                    "status": status,
                    "tasks": tasks,
                    "tasksnum": tasks_num,
                    "shownum": show_num,
                    "totaltasks": total_tasks,
                    "totaltasksnum": total_tasks_num})


@login_required(login_url="/login/")
def upload_file(request):
    """上传安装包"""
    file = request.FILES.get("caseFile")
    if file is None:
        return
    project = AppSettings.PROJECTS[request.POST.get("caseProject")]
    username = request.session.get("user")
    try:
        filepath = os.path.join(AppSettings.TESTERFOLDER, _hash_encrypted(username), project)
        # 检查文件格式
        if not file.name.endswith(".csv"):
            return "文件上传失败\n Error: File should ends with 'csv'."
        # 将文件写入到本地
        with open(os.path.join(filepath, file.name), "wb") as f:
            if file.multiple_chunks():
                [f.write(item) for item in file.chunks()]
            else:
                f.write(file.read())
        LOGGER.info("%s upload a test case file of %s" % (username, project))
        return "上传成功!!!"
    except Exception as error:
        return "文件上传失败, \n Error: %s" % traceback.format_exc()


@login_required(login_url="/login/")
def add_task(request):
    username = request.session.get("user")
    try:
        platform = request.POST.get("platform")
        filename = request.POST.get("caseFile")
        package = request.POST.get("package")
        project = request.POST.get("project")
        server = request.POST.get("server")
        status = "空闲"
        show = 0
        Task.objects.create(username=username, platform=platform, package=package, testcase=filename,
                            project=project, server=server, status=status, show=show)
        return JsonResponse("成功添加自动化测试任务", safe=False)
    except:
        return JsonResponse("添加自动化测试任务失败\nError: %s" % traceback.format_exc(), safe=False)

@login_required(login_url="/login/")
def remove_task(request):
    username = request.session.get("user")
    try:
        identify = request.POST.get("identify")
        print(identify)
        if identify == "remove":
            Task.objects.filter(Q(username=username) & Q(status="完成") & Q(show=0)).update(show=1)
        return JsonResponse("成功移除已完成的自动化测试任务", safe=False)
    except:
        return JsonResponse("移除已完成的自动化测试任务失败\nError: %s" % traceback.format_exc(), safe=False)


@login_required(login_url="/login/")
def execute(request):
    username = request.session.get("user")
    if request.is_ajax():
        task_ids = json.loads(request.POST.get("ids"))
        # 将所有申请执行的状态都改为队列
        for task_id in task_ids:
            Task.objects.filter(id=task_id).update(status="队列")
        return JsonResponse("自动化测试已经开始", safe=False)


def share(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    # 子服务器登录校验
    if not auth.authenticate(username=username, password=password):
        return JsonResponse("Login failed, username or password is wrong.", safe=False)
    single = request.POST.get("single")
    status = request.POST.get("status")
    host = request.POST.get("host")
    port = request.POST.get("port")
    try:
        server = "http://%s:%s" % (host, port)
        
        out = dbmanage.select("autotest_subserver", "id","server='%s'" % server)
        if out:
            SubServer.objects.filter(id=out[0][0]).update(server=server, single=single, status=status)
        else:
            SubServer.objects.create(username=username, server=server, single=single, status=status)

        def watching(server):
            """监控server的状态, 如果server无法连接, 则将其删除"""
            sys.stdout.write("Start watching the sub-server named %s\n" % server)
            while True:
                time.sleep(30)
                try:
                    requests.get(server)
                except:
                    SubServer.objects.filter(server=server).delete()
                    sys.stderr.write("Sub-server %s is closed, delete it.\n" % server)
                    break
            
        thread = threading.Thread(target=watching, args=(server,))
        thread.setDaemon(False)
        thread.start()
    except:
        return JsonResponse(
            "Central server gets a wrong host or port, please ask administrator for help.\n"
            "Error: %s" % traceback.format_exc(),
            safe=False)

    def get_localhost():
        """Return localhost"""
        while True:
            with suppress(Exception):
                name = socket.getfqdn(socket.gethostname())
                host = socket.gethostbyname(name)
                return host
    return JsonResponse("Connect to central server %s success" % get_localhost(), safe=False)


def update_task(request):
    id = request.POST.get("id")
    if id is not None:
        status = request.POST.get("status")
        Task.objects.filter(id=int(id)).update(status=status)
        out = dbmanage.select("autotest_task", "server", "id=%s" % id)
        if out:
            _, server = out[0][0].split("-")
            SubServer.objects.filter(server=server.strip()).update(status=0)
    return JsonResponse("Update task status success", safe=False)

