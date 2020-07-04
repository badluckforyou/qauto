import re
import time
import random
import requests
import datetime
import traceback
import ujson as json

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
    args_found = pattern.findall(code)
    # 配置之后如果有多个(), 表明传入的随机规则不正确
    if len(args_found) != 1:
        return
    for arg in args_found[0].split(", "):
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


def parse_random_data(ident, data):
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
            length, new_value = exec_code(ident, code)
            parse_data.setdefault(keyword, reset_special_character(new_value))
    except:
        traceback.print_exc()
    return length, parse_data


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


def send_request(d, method, url, data_type, headers, data):
    """发送请求"""
    try:
        send_data = json.dumps(data) if data_type != "DICT" else data
    except:
        send_data = data
    d["send_data"] = json.dumps(send_data, indent=4, ensure_ascii=False) if not isinstance(send_data, str) else send_data
    d["run_time"] = datetime.datetime.now().strftime("%X")
    start_time = time.time()
    try:
        response = requests.request(method, url, headers=headers, data=send_data)
        d["status_code"] = response.status_code
        try:
            d["recv_data"] = response.text
        except:
            d["recv_data"] = json.dumps(response.content.decode("utf-8"))
    except:
        d["status_code"] = "undefined"
        d["recv_data"] = json.dumps("Send request failed. Please check your headers or data.")
        traceback.print_exc()
    d["duration"] = "%.3fs" % (time.time() - start_time)


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
        # 随机次数的值需要检验是否为数字
        if not random_times:
            random_times = 0
        elif not random_times.isdigit():
            return JsonResponse("The type of random times must be int.", safe=False)
        result = []
        # 解析data
        with suppress(Exception):
            data = json.loads(data)
        # 解析headers
        with suppress(Exception):
            headers = json.loads(headers)
        # 随机次数为0时, 发送1次请求
        if int(random_times) == 0:
            d = dict.fromkeys(("run_time", "status_code", "duration", "send_data", "recv_data"))
            send_request(d, method, url, data_type, headers, data)
            result.append(d)
        else:
            # ident为in_order的标识符, 用于in_order方法的取值
            ident = 0
            for _ in range(int(random_times)):
                d = dict.fromkeys(("run_time", "status_code", "duration", "send_data", "recv_data"))

                length, _random_data = parse_random_data(ident, random_data)
                # ident通过余数
                if length is not None:
                    ident = (ident + 1) % length
                if isinstance(data, dict):
                    for key, value in _random_data.items():
                        with suppress(Exception):
                            update_dict(data, key.split("|"), value)

                send_request(d, method, url, data_type, headers, data)
                result.append(d)
        return HttpResponse(json.dumps(result, indent=4, ensure_ascii=False))