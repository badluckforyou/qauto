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


RANDOM_METHODS = ("random_between", "random_in", "in_order")


def random_between(ident, start, end):
    if isinstance(start, int) and isinstance(end, int):
        new_value = random.randint(start, end)
    else:
        new_value = random.uniform(float(start), float(end))
    return None, new_value


def random_in(ident, *args):
    return None, random.choice(args)


def in_order(ident, *args):
    return len(args), args[ident]


def exec_code(ident, code):
    """解析并执行对应的方法"""
    # 解析方法名
    method = code.split("(")[0].strip(" ")
    if method not in RANDOM_METHODS:
        return
    # 匹配参数的正则
    pattern = re.compile(r"\((.*?)\)$")
    args = []
    args_found = pattern.findall(code.replace(" ", ""))
    # 配置之后如果有多个(), 表明传入的随机规则不正确
    if len(args_found) != 1:
        return

    for arg in args_found[0].split(","):
        arg = arg.replace('"', "").replace("'", '"').strip(" ")
        try:
            args.append(json.loads(arg))
        except:
            args.append(arg)
    return globals()[method](ident, *args)


def replace_special_character(data):
    """将request data内的特殊字符改成其它字符"""
    if isinstance(data, str):
        special_characters = {
            r"\&": "&amp;",
            r"\,": "&#44;",
            r"\'": "&#39;",
            r'\"': "&quot;",
            r"\ ": "&nbsp;",
            r"\(": "&#40;",
            r"\)": "&#41;",
            r"\:": "&#58;",
            r"\|": "&#124;",
        }
        for k, v in special_characters.items():
            data = data.replace(k, v)
    return data


def reset_special_character(data):
    if isinstance(data, str):
        special_characters = {
            "&amp;": "&",
            "&#44;": ",",
            "&#39;": "'",
            "&quot;": '"',
            "&nbsp;": " ",
            "&#40;": "(",
            "&#41;": ")",
            "&#58;": ":",
            "&#124;": "|",
        }
        for k, v in special_characters.items():
            data = data.replace(k, v)
    return data


def parse_random_data(idents, data):
    """解析获取到的规则, 拆分关键字及要执行的代码"""
    length = None
    parse_data = {}
    try:
        for line in data.splitlines():
            # 跳过空行和注释行
            if not line or line.lstrip(" ").startswith("//"):
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


def update_dict(dictionary, array, value):
    """递归给字典赋值"""
    if not isinstance(dictionary, dict) and not isinstance(array, list):
        return
    item = array.pop(0)
    item = reset_special_character(item)
    if item not in dictionary:
        raise ValueError("%s not in %s" % (item, dictionary.keys()))
    if not array:
        dictionary[item] = value
        return
    update_dict(dictionary[item], array, value)


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


def send_request(random_times, random_data, send_type, method, url, data_type, headers, data):
    idents = {}
    request_data = []
    for _ in range(random_times if random_times != 0 else 1):
        if random_times != 0:
            _random_data = parse_random_data(idents, random_data)
            for k, v in idents.items():
                if v[1] is not None:
                    idents[k] = [(v[0] + 1) % v[1], v[1]]
            if isinstance(data, dict):
                for key, value in _random_data.items():
                    with suppress(Exception):
                        update_dict(data, key.split("|"), value)
        try:
            send_data = json.dumps(data) if data_type != "DICT" else data
        except:
            send_data = data
        request_data.append(send_data)
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
        random_data = request.POST.get("randomData")
        random_times = request.POST.get("randomTimes")
        send_type = request.POST.get("sendType")
        # 随机次数的值需要检验是否为数字
        if not random_times:
            random_times = 0
        elif not random_times.isdigit():
            return JsonResponse("The type of random times must be int.", safe=False)
        # 解析data
        with suppress(Exception):
            data = json.loads(data)
        # 解析headers
        with suppress(Exception):
            headers = json.loads(headers)
        result = send_request(int(random_times), random_data, send_type, method, url, data_type, headers, data)
        return HttpResponse(json.dumps(result, indent=4, ensure_ascii=False))