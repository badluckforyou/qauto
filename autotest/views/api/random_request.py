import re
import random
import traceback
import ujson as json

from copy import deepcopy
from contextlib import suppress

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
    with suppress(Exception):
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


def get_random_request_data(data, random_times, random_data):
    idents = {}
    request_data = []
    for _ in range(random_times):
        new_data = deepcopy(data)
        parse_data = parse_random_data(idents, random_data)
        for k, v in idents.items():
            if v[1] is not None:
                idents[k] = [(v[0] + 1) % v[1], v[1]]
        if isinstance(new_data, dict):
            for key, value in parse_data.items():
                with suppress(Exception):
                    update_dict(new_data, key.split("|"), value)
        request_data.append(new_data)
    return request_data