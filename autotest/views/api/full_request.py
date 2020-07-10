import re
import random
import traceback
import ujson as json

from copy import deepcopy
from contextlib import suppress


def exec_code(code):
    """解析参数"""
    # 匹配参数的正则
    pattern = re.compile(r"\((.*?)\)$")
    args = []
    args_found = pattern.findall(code.replace(" ", ""))
    # 配置之后如果有多个(), 表明传入的随机规则不正确
    if len(args_found) != 1:
        return

    for arg in args_found[0].split(","):
        arg = arg.replace("'", '"')
        # try:
        #     args.append(json.loads(arg))
        # except:
        #     args.append(arg)
        try:
            arg = json.loads(reset_special_character(arg))
        except:
            arg = reset_special_character(arg)
        args.append(arg)
    return args


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


def parse_full_data(data):
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
            new_value = exec_code(code)
            parse_data.setdefault(keyword, new_value)
    except:
        traceback.print_exc()
    return list(parse_data.keys()), parse_data


def update_dict(data, keys, value, ident=0):
    """通过递归对字典进行更新"""
    if ident + 1 == len(keys):
        data[keys[ident]] = value
        return
    if keys[ident] in data:
        update_dict(data[keys[ident]], keys, value, ident + 1)


def get_request_data(keys, full_data, data, ident=0):
    for v in full_data[keys[ident]]:
        new_data = deepcopy(data)
        # key值特殊字符还原及子key值的拆分
        new_keys = [reset_special_character(key) for key in keys[ident].split("|")]
        with suppress(Exception):
            # 拆分后如果大于1, 则需要通过递归去查找子key再进行赋值
            # 等于1则直接赋值
            if len(new_keys) > 1:
                update_dict(new_data, new_keys, v)
            else:
                new_data[new_keys[0]] = v
        # 当keys遍历完时, 表明已经完成赋值, yiled
        if ident + 1 == len(keys):
            yield new_data
        else:
            yield from get_request_data(keys, full_data, new_data, ident + 1)


def get_full_request_data(data, full_data):
    keys, full_data = parse_full_data(full_data)
    request_data = list(get_request_data(keys, full_data, data))
    return request_data


