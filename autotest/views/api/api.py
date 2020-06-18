import re
import time
import random
import requests
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


def parse_request_data(data):
    try:
        parse_data = []
        for line in data.splitlines():
            if not line or "// " in line:
                continue
            parse_data.append(line)
        data = "".join(parse_data).replace("'", '"')
        return json.loads(r"%s" % data.replace(",}", "}"))
    except Exception as exc:
        traceback.print_exc()


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


def parse_random_data(ident, data):
    parse_data = {}
    try:
        for line in data.splitlines():
            if not line or "//" in line:
                continue
            split_line = line.split(":")
            if len(split_line) == 1:
                continue
            elif len(split_line) > 2:
                keyword, *code = split_line
                code = ":".join(code)
            else:
                keyword, code = split_line
            length, new_value = exec_code(ident, code)
            parse_data.setdefault(keyword, new_value)
    except:
        traceback.print_exc()
    return length, parse_data


def update_dict(dictionary, array, value):
    """递归给字典赋值"""
    item = array.pop(0)
    if item not in dictionary:
        raise ValueError("%s not in %s" % (item, dictionary.keys()))
    if not array:
        dictionary[item] = value
        return
    update_dict(dictionary[item], array, value)


@login_required(login_url="/login/")
def api_testing(request):
    return render(request, "templates/api/api.html", {
                    "company": AppSettings.COMPANY,
                    "methods": AppSettings.METHODS,
                    "username": request.session.get("user")})


@login_required(login_url="/login/")
def request(request):
    if request.is_ajax():
        url = request.POST.get("url")
        request_data = request.POST.get("data")
        random_data = request.POST.get("randomData")
        random_times = request.POST.get("randomTimes")
        if random_times is None:
            random_times = 1
        elif not random_times.isdigit():
            return JsonResponse("The type of random times must be int.", safe=False)
        result = []
        ident = 0
        for _ in range(int(random_times)):
            d = {}
            try:
                try:
                    data = parse_request_data(request_data)
                except:
                    data = json.loads(request_data)
                if data is None:
                    d.setdefault("Message", "Wrong request data.")
                    continue
                length, _random_data = parse_random_data(ident, random_data)

                for key, value in _random_data.items():
                    with suppress(Exception):
                        update_dict(data["data"], key.split("|"), value)

                start_time = time.time()

                if "data-type" in data and data["data-type"] == 'json':
                    req_data = json.dumps(data["data"])
                else:
                    req_data = data["data"]
                
                response = requests.request(data["method"], url, headers=data["headers"], data=req_data)

                d.setdefault("duration", "%.3fs" % (time.time() - start_time))
                d.setdefault("status_code", response.status_code)
                try:
                    d.setdefault("data", json.loads(response.text))
                except:
                    d.setdefault("data", "%s ..." % response.text[:200])
                if length is not None:
                    ident = (ident + 1) % length
            except:
                traceback.print_exc()
            result.append(d)
        return JsonResponse(json.dumps(result, indent=4, ensure_ascii=False), safe=False)