import re
import time
import random
import asyncio
import aiohttp
import requests
import datetime
import traceback
import ujson as json

from queue import Queue
from contextlib import suppress

from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from autotest.app_settings import AppSettings
from .random_request import get_random_request_data
from .full_request import get_full_request_data


def parse_full_data(idents, data):
    """解析获取到的规则, 拆分关键字及要执行的代码"""
    length = None
    parse_data = {}
    try:
        for line in data.splitlines():
            # 跳过空行和注释行
            if "in_order" not in line:
                continue
            line = replace_special_character(line)
            # 尝试拆分关键字及要执行的代码
            split_line = line.split(":")
            # 进行长度验证
            if len(split_line) == 2:
                keyword, code = split_line
            else:
                continue
            if keyword not in idents:
                idents.setdefault(keyword, [0, 0])
            ident = idents[keyword][0]
            length, new_value = exec_code(ident, code)
            idents[keyword] = [ident, length]
            parse_data.setdefault(keyword, reset_special_character(new_value))
    except:
        traceback.print_exc()
    return parse_data


class AsyncRequest:

    def __init__(self, method, url, headers, data, queue):
        self.method = method
        self.url = url
        self.headers = headers
        self.data = data
        self.queue = queue
        self.result = []

    async def _async_request(self, data):
        record = dict.fromkeys(("run_time", "status_code", 
                                "duration", "send_data", "recv_data"))

        async with aiohttp.ClientSession() as session:
            record["send_data"] = json.dumps(data) if not isinstance(data, str) else data
            record["run_time"] = datetime.datetime.now().strftime("%X")
            start_time = time.time()
            try:
                response = await session.request(self.method, self.url, headers=self.headers, data=data, ssl=False)
                record["status_code"] = response.status
                try:
                    record["recv_data"] = await response.text()
                except:
                    record["recv_data"] = json.dumps(await response.text())
            except:
                record["status_code"] = "undefined"
                record["recv_data"] = json.dumps("Send request failed. Please check your headers or data.")
                traceback.print_exc()
            record["duration"] = "%.3fs" % (time.time() - start_time)
        self.result.append(record)

    async def async_request(self):
        request_tasks = [asyncio.create_task(self._async_request(d))
                                for d in self.data]
        for request_task in request_tasks:
            await request_task
        self.queue.put(self.result)


def normal_request(method, url, headers, request_data):
    """发送请求"""
    result = []
    for data in request_data:
        record = dict.fromkeys(("run_time", "status_code", 
                                "duration", "send_data", "recv_data"))
        record["send_data"] = json.dumps(data) if not isinstance(data, str) else data
        record["run_time"] = datetime.datetime.now().strftime("%X")
        start_time = time.time()
        try:
            response = requests.request(method, url, headers=headers, data=data)
            record["status_code"] = response.status_code
            try:
                record["recv_data"] = response.text
            except:
                record["recv_data"] = json.dumps(response.content.decode("utf-8"))
        except:
            record["status_code"] = "undefined"
            record["recv_data"] = json.dumps("Send request failed. Please check your headers or data.")
            traceback.print_exc()
        record["duration"] = "%.3fs" % (time.time() - start_time)
        result.append(record)
    return result


def async_request(method, url, headers, request_data):
    queue = Queue()
    request = AsyncRequest(method, url, headers, request_data, queue)
    asyncio.run(request.async_request())
    return queue.get()


def send_request(
        send_type,
        method, 
        url, 
        data_type, 
        headers, 
        data, 
        random_times=None, 
        random_data=None, 
        full_data=None):
    if random_times is not None and full_data is None:
        request_data = get_random_request_data(data, int(random_times), random_data)
    elif random_times is None and full_data is not None:
        request_data = get_full_request_data(data, full_data)
    else:
        request_data = [data]
    if send_type == "asynchronous":
        return async_request(method, url, headers, request_data)
    elif send_type == "synchronous":
        return normal_request(method, url, headers, request_data)


# @login_required(login_url="/login/")
def api_testing(request):
    return render(request, "templates/api/api.html", {
                    "title": AppSettings.TITLE,
                    "company": AppSettings.COMPANY,
                    "methods": AppSettings.METHODS,
                    "datatype": AppSettings.DATATYPE,
                    "username": request.session.get("user")})


# @login_required(login_url="/login/")
def request(request):
    if request.is_ajax():
        url = request.POST.get("url")
        method = request.POST.get("method")
        headers = request.POST.get("headers")
        data_type = request.POST.get("dataType")
        data = request.POST.get("data")
        send_type = request.POST.get("sendType")
        random_data = request.POST.get("randomData") or None
        random_times = request.POST.get("randomTimes") or None
        full_data = request.POST.get("fullData") or None
        # 随机次数校验
        if random_times is not None and not random_times.isdigit():
            return JsonResponse("The type of random times must be int.", safe=False)
        # 解析data
        with suppress(Exception):
            data = json.loads(data)
        # 解析headers
        with suppress(Exception):
            headers = json.loads(headers)
        if random_times is None and full_data is not None:
            result = send_request(
                send_type,
                method,
                url,
                data_type,
                headers,
                data,
                full_data=full_data
            )
        elif full_data is None and random_times is not None:
            result = send_request(
                send_type,
                method,
                url,
                data_type,
                headers,
                data,
                random_times=int(random_times),
                random_data=random_data
            )
        else:
            result = send_request(
                send_type,
                method,
                url,
                data_type,
                headers,
                data
            )
        return HttpResponse(json.dumps(result, indent=4, ensure_ascii=False))