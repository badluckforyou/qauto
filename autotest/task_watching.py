import os
import sys
import time
import ujson as json
import requests
import traceback

from copy import deepcopy

from autotest.database import dbmanage
from autotest.models import Task, SubServer
from autotest.app_settings import AppSettings
from autotest.helper import _hash_encrypted
from autotest.csv import parse_csv



def get_tasks():
    """
    从数据库中获取tasks数据
    returns:
        None or tasks: {
                    "执行": {
                        "子服务器": ["任务id"],
                        ...
                    },
                    "队列": {
                        "子服务器": ["任务id"],
                        ...
                    }
                }
    """
    init_tasks = {
        "队列": {},
        "执行": {}
    }
    tasks = deepcopy(init_tasks)
    out = dbmanage.select("autotest_task", "id, server, status", "status='执行' or status='队列'")
    if out:
        servers = list(set([s[1] for s in out]))
        for status in ["队列", "执行"]:
            data = {}
            for server in servers:
                ids = []
                for id, _server, _status in out:
                    if status == _status and server == _server:
                        ids.append(id)
                if ids:
                    data.setdefault(server, ids)
            tasks[status] = data
    return tasks if tasks != init_tasks else None


def delay(s):
    time.sleep(s)

        
def execute_tasks(id):
    """
    根据任务id 去执行对应的测试任务
    """
    try:
        # 开始前更新任务状态为执行
        Task.objects.filter(id=id).update(status="执行")
        # 获取任务的相关数据并提取
        out = dbmanage.select("autotest_task", keywords="id=%s" % id)
        _, username, project, platform, package, filename, server, _, _ = out[0]
        project = AppSettings.PROJECTS[project]
        #获取测试用例文件并解析成规定格式的数据
        file = os.path.join(AppSettings.TESTERFOLDER, _hash_encrypted(username), project, filename)
        testcase = parse_csv(file)

        try:
            _, server = server.split(' - ')
        except:
            traceback.print_exc()
            Task.objects.filter(id=id).update(status="空闲")
            return
        try:
            requests.get(server)
        except:
            traceback.print_exc()
            # 如果子服务器无法连接, 则表明服务器已经关闭, 中断测试并将该数据删除
            SubServer.objects.filter(server=server).delete()
            Task.objects.filter(id=id).update(status="空闲")
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
        Task.objects.filter(id=id).update(status="空闲")


def watching():
    """
    任务监控, 定时去获取任务池
    如果有任务则去执行任务
    """
    sys.stdout.write("Start watching tasks ... \n")
    while True:
        delay(15)
        tasks = get_tasks()
        # 没有任务则直接延迟30秒, 并且跳过后续操作
        if tasks is None:
            delay(15)
            continue
        # 如果没有队列数据, 则表明无需对现有任务进行改动, 直接跳过后续操作
        if not tasks["队列"]:
            continue
        for server, ids in tasks["队列"].items():
            # 如果子服务器已经有正在执行的测试任务, 便直接跳过
            if server in tasks["执行"].keys():
                continue
            # 执行第1个测试任务即可
            execute_tasks(ids[0])

