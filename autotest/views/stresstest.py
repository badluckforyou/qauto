#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: luzhiqi
# @Email: luzhiqi@ijunhai.com
# @Date: 2020-02-09 17:57:40
# @LastEditor: luzhiqi
# @LastEditTime: 2020-04-3 17:23:23



import os
import sys
import json
import logging
import traceback
import threading

from contextlib import suppress

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from autotest.readsteps import read_steps
from autotest.app_settings import AppSettings
from autotest.database import DataBaseManage
from autotest.remote import CommandIssue
from autotest.management import Management, DockerNumberError, DeviceNumberError


LOGGER = logging.getLogger("autotest")


def get_all_files(folder, result):
    """递归获取所有文件名"""
    for file in os.listdir(folder):
        file = os.path.join(folder, file)
        if os.path.isdir(file):
            get_all_files(file, result)
        else:
            result.append(file)
    return result


def get_files(username, game=None):
    """
    根据传参的数量来决定返回的内容
    """
    filepath = os.path.join(AppSettings.TESTERFOLDER, username)
    filepath = os.path.join(filepath, game) if game else filepath
    apks = list()
    images = list()
    for file in get_all_files(filepath, []):
        # 获取文件名
        end = os.path.splitext(file)[-1]
        file = file.split("\\")[-1]
        if end == ".apk":
            apks.append(file)
        elif end == ".png":
            images.append(file)
    if not apks:
        apks.append("未发现安装包")
    return apks, images


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


def upload_file(filepath, file):
    """上传文件的写入"""
    with open(os.path.join(filepath, file.name), "wb") as f:
        if file.multiple_chunks():
            [f.write(item) for item in file.chunks()]
        else:
            f.write(file.read())


@login_required(login_url="/login/")
def stress(request):
    """执行自动化压力测试界面"""
    username = request.session.get("user")
    default_game = "所有游戏"
    message = None
    if request.GET:
        # 测试人员选择了具体的游戏后, 安装包及步聚表只显示该游戏的
        game = AppSettings.GAMES[request.GET.get("game")]
        apks, images = get_files(username, game) if game else get_files(username)
    else:
        if request.POST:
            if request.FILES.get("apk") is not None:
                message = upload_apk(request)
            elif request.FILES.get("steps") is not None:
                message = upload_steps(request)
            elif request.FILES.get("images") is not None:
                message = upload_images(request)
            else:
                pass
        apks, images = get_files(username)

    return render(request, "templates/stresstest.html", {
                    "title": AppSettings.TITLE,
                    "company": AppSettings.COMPANY,
                    "username": username,
                    "default_game": default_game,
                    "message": message,
                    "apks": apks,
                    "images": [""] + images,
                    "games": AppSettings.GAMES.keys(),
                    "resolutions": AppSettings.RESOLUTIONS})


@login_required(login_url="/login/")
def upload_apk(request):
    """上传安装包"""
    apk = request.FILES.get("apk")
    game = AppSettings.GAMES[request.POST.get("apkGame")]
    username = request.session.get("user")
    try:
        apkpath = os.path.join(AppSettings.TESTERFOLDER, username, game, "apk")
        # 把旧包删除掉
        remove_file(apkpath, ".apk")
        if not apk.name.endswith(".apk"):
            return "文件上传失败\n Error: File should ends with 'apk'."
        upload_file(apkpath, apk)
        LOGGER.info("%s upload an apk of %s" % (username, game))
        return "上传成功!!!"
    except Exception as error:
        traceback.print_exc()
        return "文件上传失败, 请联系管理员查看报错!!"


@login_required(login_url="/login/")
def upload_steps(request):
    steps = request.FILES.get("steps")
    game = AppSettings.GAMES[request.POST.get("stepsGame")]
    username = request.session.get("user")
    try:
        stepspath = os.path.join(AppSettings.TESTERFOLDER, username, game, "steps")
        remove_file(stepspath, [".xls", ".xlsx", ".py"])
        if not steps.name.endswith(".xls") and not steps.name.endswith(".xlsx") \
                                                    and not steps.name.endswith(".py"):
            return "文件上传失败\n Error: File shoud ends with 'xls', 'xlsx' or 'py'."
        upload_file(stepspath, steps)
        LOGGER.info("%s upload a steps file of %s" % (username, game))
        return "上传成功!"
    except Exception as error:
        traceback.print_exc()
        return "文件上传失败, 请联系管理员查看报错!!"


@login_required(login_url="/login/")
def upload_images(request):
    """上传图片"""
    images = request.FILES.getlist("images")
    game = AppSettings.GAMES[request.POST.get("imagesGame")]
    username = request.session.get("user")
    try:
        imagespath = os.path.join(AppSettings.TESTERFOLDER, username, game, "images")
        # 传输前需要确认照片是否以.png结尾
        for image in images:
            if not image.name.endswith(".png"):
                return "图片上传失败\n Error: File shoud ends with 'png'."
        remove_file(imagespath, ".png")
        # 照片传输
        [upload_file(imagespath, image) for image in images]
        LOGGER.info("%s upload some images of %s" % (username, game))
        return "上传成功!"
    except Exception as error:
        traceback.print_exc()
        return "图片上传失败, 请联系管理员查看报错!!"

@login_required(login_url="/login/")
def uninstall(request):
    username = request.session.get("user")
    if request.is_ajax():
        if username in Management.INUSE.keys() and Management.INUSE[username] is True:
            return JsonResponse("""
无法进行卸载操作
Error: A stress test or apk operation is under way.
""", safe=False)

        dev_number = request.POST.get("choDevNum")
        if not dev_number:
            dev_number = request.POST.get("setDevNum")
            # 如果不是纯数字, 则表明测试人员输入的设备数有问题
            if not dev_number.isdigit():
                return JsonResponse("设备数量有误, 请重新输入!!!", safe=False)

        package = request.POST.get("package")

        data = "TESTER='%s', OPERATION='install', PACKAGE='%s'" % (username, package)
        # 把数据更新到数据库中
        db = DataBaseManage()
        out = db.select("autotest_apkmanage", "id", "TESTER='%s'" % username)
        if out:
            db.update("autotest_apkmanage", data, "id=%s" % out[0][0])
        elif out is False:
            return JsonResponse(
                "出现了预期以外的错误, 请联系管理员处理\n"
                "Error: Can't connect to MySQL server.",
                safe=False
            )
        else:
            db.insert("autotest_apkmanage", data)

        try:
            Management.check_devices_for_start(username, dev_number)
        except DockerNumberError:
            return JsonResponse("""
无法进行卸载操作
Error: Dockers are not enough.
""", safe=False)
        except DeviceNumberError:
            return JsonResponse("""
无法进行卸载操作
Error: Devices are not enough.
""", safe=False)
        else:
            sys.stdout.write("%s try to uninstall %s\n" % (username, package))
            LOGGER.info("%s try to uninstall %s" % (username, package))
            # 设备需求小于等于500台时, useall=False, 反之则useal=True.
            if int(dev_number) <= 500:
                Management.start_test("apkmanage.py", username, dev_number, useall=False)
            else:
                Management.start_test("apkmanage.py", username, dev_number)
            watching_thread = threading.Thread(target=Management.watching, args=(username,))
            watching_thread.start()
        return JsonResponse("已开始卸载%s!!!" % package, safe=False)


@login_required(login_url="/login/")
def fuzzy_uninstall(request):
    username = request.session.get("user")
    if request.is_ajax():
        if username in Management.INUSE.keys() and Management.INUSE[username] is True:
            return JsonResponse("""
无法进行卸载操作
Error: A stress test or apk operation is under way.
""", safe=False)

        dev_number = request.POST.get("choDevNum")
        if not dev_number:
            dev_number = request.POST.get("setDevNum")
            # 如果不是纯数字, 则表明测试人员输入的设备数有问题
            if not dev_number.isdigit():
                return JsonResponse("设备数量有误, 请重新输入!!!", safe=False)

        package = request.POST.get("package")

        data = "TESTER='%s', OPERATION='fuzzy_uninstall', PACKAGE='%s'" % (username, package)
        # 把数据更新到数据库中
        db = DataBaseManage()
        out = db.select("autotest_apkmanage", "id", "TESTER='%s'" % username)
        if out:
            db.update("autotest_apkmanage", data, "id=%s" % out[0][0])
        elif out is False:
            return JsonResponse(
                "出现了预期以外的错误, 请联系管理员处理\n"
                "Error: Can't connect to MySQL server.",
                safe=False
            )
        else:
            db.insert("autotest_apkmanage", data)

        try:
            Management.check_devices_for_start(username, dev_number)
        except DockerNumberError:
            return JsonResponse("""
无法进行卸载操作
Error: Dockers are not enough.
""", safe=False)
        except DeviceNumberError:
            return JsonResponse("""
无法进行卸载操作
Error: Devices are not enough.
""", safe=False)
        else:
            sys.stdout.write("%s try to fuzzy uninstall %s\n" % (username, package))
            LOGGER.info("%s try to fuzzy uninstall %s" % (username, package))
            # 设备需求小于等于500台时, useall=False, 反之则useal=True.
            if int(dev_number) <= 500:
                Management.start_test("apkmanage.py", username, dev_number, useall=False)
            else:
                Management.start_test("apkmanage.py", username, dev_number)
            watching_thread = threading.Thread(target=Management.watching, args=(username,))
            watching_thread.start()
        return JsonResponse("已开始模糊卸载%s!!!" % package, safe=False)


@login_required(login_url="/login/")
def install(request):
    username = request.session.get("user")
    if request.is_ajax():
        if username in Management.INUSE.keys() and Management.INUSE[username] is True:
            return JsonResponse("""
无法进行安装操作
Error: A stress test or apk operation is under way.
""", safe=False)

        dev_number = request.POST.get("choDevNum")
        if not dev_number:
            dev_number = request.POST.get("setDevNum")
            # 如果不是纯数字, 则表明测试人员输入的设备数有问题
            if not dev_number.isdigit():
                return JsonResponse("设备数量有误, 请重新输入!!!", safe=False)

        apk = request.POST.get("apk")
        package = request.POST.get("package")

        data = "TESTER='%s', OPERATION='install', APK='%s', package='%s'" % (username, apk, package)
        # 把数据更新到数据库中
        db = DataBaseManage()
        out = db.select("autotest_apkmanage", "id", "TESTER='%s'" % apk)
        if out:
            db.update("autotest_apkmanage", data, "id=%s" % out[0][0])
        elif out is False:
            return JsonResponse(
                "出现了预期以外的错误, 请联系管理员处理\n"
                "Error: Can't connect to MySQL server.",
                safe=False
            ) 
        else:
            db.insert("autotest_apkmanage", data)

        try:
            Management.check_devices_for_start(username, dev_number)
        except DockerNumberError:
            return JsonResponse("""
无法进行安装操作
Error: Dockers are not enough.
""", safe=False)
        except DeviceNumberError:
            return JsonResponse("""
无法进行安装操作
Error: Devices are not enough.
""", safe=False)
        else:
            sys.stdout.write("%s try to install %s\n" % (username, package))
            LOGGER.info("%s try to install %s" % (username, package))
            # 设备需求小于等于500台时, useall=False, 反之则useal=True.
            if int(dev_number) <= 500:
                Management.start_test("apkmanage.py", username, dev_number, useall=False)
            else:
                Management.start_test("apkmanage.py", username, dev_number)
            watching_thread = threading.Thread(target=Management.watching, args=(username,))
            watching_thread.start()
        return JsonResponse("已开始安装%s!!!" % package, safe=False)


@login_required(login_url="/login/")
def execute(request):
    username = request.session.get("user")
    if request.is_ajax():
        # 先检测测试人员当前是否已经有需求在执行中了
        if username in Management.INUSE.keys() and Management.INUSE[username] is True:
            return JsonResponse(
                "未能成功启动压测\n"
                "Error: A stress test or apk operation is under way.",
                safe=False
            )

        game = AppSettings.GAMES[request.POST.get("game")]
        dev_number = request.POST.get("choDevNum")
        if not dev_number:
            dev_number = request.POST.get("setDevNum")
            # 如果不是纯数字, 则表明测试人员输入的设备数有问题
            if not dev_number.isdigit():
                return JsonResponse("设备数量有误, 请重新输入!!!", safe=False)

        try:
            # 先尝试从resolution中获取分辨率
            resolution = tuple(int(i) for i in request.POST.get("resolution").split(" × "))
        except ValueError:
            # 如果获取失败, 则表明测试人员是自己输入的分辨率
            try:
                resolution = (int(request.POST.get("resol_x")), int(request.POST.get("resol_y")))
            except:
                resolution = set()
        except:
            resolution = set()

        # 需要再次确认分辨率的长度是否为2
        resolution = None if len(resolution) != 2 else resolution
        
        # stepspath = os.path.join(AppSettings.TESTERFOLDER, username, game, "steps")
        # steps = read_steps(stepspath)
        # print(steps)
        # if isinstance(steps, str):
        #     return JsonResponse(steps, safe=False)

        # 检查图片格式
        image = request.POST.get("retry")
        if image and not image.endswith(".png"):
            return JsonResponse("重试图片非以.png结尾, 请重新选择!!!", safe=False)

        # 检查等级格式
        level = request.POST.get("level")
        if level and not level.isdigit():
            return JsonResponse("等级仅可为数字, 请重新输入!!!", safe=False)

        # 检查执行时长格式
        runtime = request.POST.get("runtime")
        if runtime and not runtime.isdigit():
            return JsonResponse("时长仅可为数字, 请重新输入!!!", safe=False)
        # 有可能传入的是0, 因此不能用not runtime
        elif runtime is None:
            runtime = 2

        data = (
            "TESTER='%(tester)s', "
            "GAME='%(game)s',"
            "RESOLUTION='%(resolution)s', "
            "RETRY_IMAGE=%(image)s, "
            "PACKAGE='%(package)s', "
            "LEVEL=%(level)s, "
            "RUNTIME=%(time)s"
        ) % {
            "tester": username,
            "game": game,
            "resolution": json.dumps(resolution),
            "image": json.dumps(image),
            "package": request.POST.get("package"),
            "level": json.dumps(level),
            "time": json.dumps(runtime),
        }
        # 把数据更新到数据库中
        db = DataBaseManage()
        out = db.select("autotest_stress", "id", "TESTER='%s'" % username)
        if out:
            db.update("autotest_stress", data, "id=%s" % out[0][0])
        elif out is False:
            return JsonResponse(
                "出现了预期以外的错误, 请联系管理员处理\n"
                "Error: Can't connect to MySQL server.",
                safe=False
            )
        else:
            db.insert("autotest_stress", data)

        # 检查空闲云手机是否足够, 以防其它部内也在占用着云手机, 不足够直接返回
        try:
            Management.check_devices_for_start(username, dev_number)
        except DockerNumberError:
            return JsonResponse(
                "未能成功启动压测\n"
                "Error: Dockers are not enough.",
                safe=False 
            )
        except DeviceNumberError:
            return JsonResponse(
                "未能成功启动压测\n"
                "Error: Devices are not enough.",
                safe=False
            )
        except ConnectionError:
            return JsonResponse(
                "出现了预期以外的错误, 请联系管理员处理\n"
                "Error: Can't connect to MySQL server.",
                safe=False
            )
        else:
            sys.stdout.write("%s try to execute a stress test of %s\n" % (username, game))
            LOGGER.info("%s try to execute a stress test of %s" % (username, game))
            # 设备需求小于等于500台时, useall=False, 反之则useal=True.
            if int(dev_number) <= 500:
                Management.start_test("stress.py", username, dev_number, useall=False)
            else:
                Management.start_test("stress.py", username, dev_number)
            # 监控执行时长
            watching_thread = threading.Thread(target=Management.watching, args=(username, runtime))
            watching_thread.start()
       
        LOGGER.info("%s try to execute a stress test of %s" % (username, game))
        return JsonResponse("自动化压力测试已开始执行!!!", safe=False)


@login_required(login_url="/login/")
def stop(request):
    username = request.session.get("user")
    if request.is_ajax():
        stop = request.POST.get("stop")
        if stop == "stop":
            if username not in Management.INUSE.keys():
                return JsonResponse("没有正在执行的自动化压力测试任务!!!", safe=False)
            Management.stop_test(username)
            return JsonResponse("自动化压力测试已停止!!!", safe=False)
        else:
            return JsonResponse("中断失败, 请联系管理员查找原因!!!", safe=False)
