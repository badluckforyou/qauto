import os
import sys
import time
import ujson as json
import datetime
import requests
import traceback
import threading

from copy import deepcopy

from autotest.query import select_task
from autotest.models import Task, SubServer, Log
from autotest.app_settings import AppSettings
from autotest.helper import _hash_encrypted, current_time
from autotest.csv import parse_csv


QUEUEING = "队列"
RUNNING = "执行"
FREE = "空闲"


def get_tasks():
    """
    从数据库中获取tasks数据
    returns:
        None or tasks
    tasks: {
        "执行": {
            "子服务器": [
                    ["任务id", "执行时间"],
                    ...
                ],
            ...
        },
        "队列": {
            "子服务器": [
                    ["任务id", "执行时间"],
                    ...
                ],
            ...
        }
    }
    """
    init = dict.fromkeys((QUEUEING, RUNNING), {})
    result = deepcopy(init)

    tasks_query = {"wants": "id, server, status, executetime",
                    "condition": "status='执行' or status='队列'"}
    tasks = select_task(**tasks_query)
    
    if tasks:
        s = {}
        for id, server, status, time in tasks:
            t = []
            t.append(id)
            t.append(time)
            if status == RUNNING:
                result[RUNNING] = {server: [t]}
                break
            if server not in result[QUEUEING]:
                s.setdefault(server, [t])
            else:
                s[server].append(t)
            result[QUEUEING] = s
    return result if result != init else None


def delay(s):
    time.sleep(s)

        
def execute_task(id):
    """
    根据任务id 去执行对应的测试任务
    """
    try:
        # 开始前更新任务状态为执行
        Task.objects.filter(id=id).update(status=RUNNING)
        # 获取任务的相关数据并提取
        star_query = {"condition": "id=%s" % id}
        _, username, project, platform, package, filename, server, _, _, _ = select_task(**star_query)[0]
        project = AppSettings.PROJECTS[project]
        #获取测试用例文件并解析成规定格式的数据
        file = os.path.join(AppSettings.TESTERFOLDER, _hash_encrypted(username), project, filename)
        testcase = parse_csv(file)
        log = {"username": username,
                "logname": "任务开始",
                "recordtime": current_time(),
                "data": "的任务开始执行, 任务编号%s" % id}
        Log.objects.create(**log)
        try:
            _, server = server.split(' - ')
        except:
            traceback.print_exc()
            Task.objects.filter(id=id).update(status=FREE)
            log["logname"] = "任务失败"
            log["data"] = "的任务出错, 中断执行, 任务编号%s" % id
            Log.objects.create(**log)
            return
        try:
            requests.get(server)
        except:
            traceback.print_exc()
            # 如果子服务器无法连接, 则表明服务器已经关闭, 中断测试并将该子服务器删除
            SubServer.objects.filter(server=server).delete()
            Task.objects.filter(id=id).update(status=FREE)
            log["logname"] = "任务失败"
            log["data"] = "的任务出错, 中断执行, 任务编号%s" % id
            Log.objects.create(**log)
            return
        # 生成数据并发送给子服务器以唤起自动化任务
        data = {
            "id": id,
            "username": username,
            "project": project,
            "platform": platform,
            "package": package,
            "testcase": testcase
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
        response = requests.post(server, data=json.dumps(data), headers=headers)
        # 执行自动化测试期间需要将子服务器状态设置为不可见
        SubServer.objects.filter(server=server).update(status=1)
    except:
        traceback.print_exc()
        Task.objects.filter(id=id).update(status=FREE)


def watching():
    """
    任务监控, 定时去获取任务池
    如果有任务则去执行任务
    """
    # sys.stdout.write("Start watching tasks ... \n")
    while True:
        # 请求不能过于频繁, 因此增加delay
        delay(15)
        tasks = get_tasks()
        # 没有任务则多延迟15秒, 并且跳过后续操作
        if tasks is None:
            delay(15)
            continue
        # 如果没有队列数据, 则表明无需对现有任务进行改动, 直接跳过后续操作
        if not tasks[QUEUEING]:
            continue
        for server, tasksinfo in tasks[QUEUEING].items():
            # 如果子服务器已经有正在执行的测试任务, 便直接跳过
            if server in tasks[RUNNING].keys():
                continue
            for id, exectime in tasksinfo:

                exectime = time.mktime(time.strptime(exectime, "%Y-%m-%d %X"))
                # 如果任务执行时间大于当前时间, 表明其为定时任务, 可直接跳过
                if exectime - time.time() > 0:
                    continue
                execute_task(id)