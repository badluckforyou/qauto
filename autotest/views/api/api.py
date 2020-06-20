import re
import time
import random
import requests
import datetime
import traceback
import ujson as json

from contextlib import suppress

from django.shortcuts import render
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
    method = code.split("(")[0].strip(" ")
    if method not in RANDOM_METHODS:
        raise ValueError("%s" % method)
    pattern = re.compile(r"\((.*?)\)$")
    args = []
    args_found = pattern.findall(code)
    if len(args_found) != 1:
        raise ValueError("%s" % args_found)
    for arg in args_found[0].split(", "):
        arg = arg.replace('"', "").replace("'", '"').strip(" ")
        try:
            args.append(json.loads(arg))
        except:
            args.append(arg)
    return globals()[method](ident, *args)


def replace_special_character(data):
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
            "&lsb;": "[",
            "&rsb;": "]",
            "&#58;": ":",
            "&#124;": "|",
        }
        for k, v in special_characters.items():
            data = data.replace(k, v)
    return data


def parse_random_data(ident, data):
    parse_data = {}
    try:
        for line in data.splitlines():
            if not line or line.lstrip(" ").startswith("//"):
                continue
            line = replace_special_character(line)
            split_line = line.split(":")
            if len(split_line) == 1:
                continue
            elif len(split_line) == 2:
                keyword, code = split_line
            else:
                raise ValueError
            length, new_value = exec_code(ident, code)
            parse_data.setdefault(keyword, reset_special_character(new_value))
    except:
        traceback.print_exc()
    return length, parse_data


def update_dict(dictionary, array, value):
    """递归给字典赋值"""
    item = array.pop(0)
    item = reset_special_character(item)
    if item not in dictionary:
        raise ValueError("%s not in %s" % (item, dictionary.keys()))
    if not array:
        dictionary[item] = value
        return
    update_dict(dictionary[item], array, value)


@login_required(login_url="/login/")
def api_testing(request):
    return render(request, "templates/api/api.html", {
                    "title": AppSettings.TITLE,
                    "company": AppSettings.COMPANY,
                    "methods": AppSettings.METHODS,
                    "datatype": AppSettings.DATATYPE,
                    "username": request.session.get("user")})


@login_required(login_url="/login/")
def request(request):
    if request.is_ajax():
        url = request.POST.get("url")
        method = request.POST.get("method")
        headers = request.POST.get("headers")
        data_type = request.POST.get("dataType")
        data = request.POST.get("data")
        random_data = request.POST.get("randomData")
        random_times = request.POST.get("randomTimes")
        if random_times is None:
            random_times = 1
        elif not random_times.isdigit():
            return JsonResponse("The type of random times must be int.", safe=False)
        result = []
        error = ""
        try:
            data = json.loads(data.replace("'", '"'))
        except:
            error += "Get wrong data  %s ." % data

        try:
            headers = json.loads(headers.replace("'", '"'))
        except:
            error += "Get wrong headers %s |" % headers

        if int(random_times) == 0:
            d = {}
            with suppress(Exception):
                data = json.dumps(data) if data_type == "json" else data
            
            d.setdefault("run_time", datetime.datetime.now().strftime("%Y-%m-%d %X"))
            start_time = time.time()
            try:
                response = requests.request(method, url, headers=headers, data=data)
                d.setdefault("status_code", response.status_code)
                try:
                    d.setdefault("data", json.loads(response.text))
                except:
                    d.setdefault("data", "%s ..." % response.text[:200])
            except:
                    d.setdefault("data", "%sSend request failed" % error)
            d.setdefault("duration", "%.3fs" % (time.time() - start_time))
            result.append(d)
        else:
            ident = 0
            for _ in range(int(random_times)):
                d = {}
                length, _random_data = parse_random_data(ident, random_data)

                if isinstance(data, dict):
                    for key, value in _random_data.items():
                        with suppress(Exception):
                            update_dict(data, key.split("|"), value)

                with suppress(Exception):
                    data = json.dumps(data) if data_type == "json" else data

                d.setdefault("run_time", datetime.datetime.now().strftime("%Y-%m-%d %X"))
                start_time = time.time()
                try:
                    response = requests.request(method, url, headers=headers, data=data)
                    d.setdefault("status_code", response.status_code)
                    try:
                        d.setdefault("data", json.loads(response.text))
                    except:
                        d.setdefault("data", "%s ..." % response.text[:200])
                except:
                    d.setdefault("data", "%sSend request failed" % error)
                d.setdefault("duration", "%.3fs" % (time.time() - start_time))
                if length is not None:
                    ident = (ident + 1) % length
                result.append(d)
        return JsonResponse(json.dumps(result, indent=4, ensure_ascii=False), safe=False)