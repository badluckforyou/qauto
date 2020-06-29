import os
import hashlib
import datetime

from autotest.app_settings import AppSettings


def current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %X")


def _hash_encrypted(entry):
    """md5加密"""
    _hash = hashlib.md5()
    _hash.update(entry.encode("utf-8"))
    return _hash.hexdigest()


def get_specified_files(filepath, key):
    for file in os.listdir(filepath):
        file = os.path.join(filepath, file)
        if os.path.isdir(file):
            yield from get_specified_files(file, key)
        elif file.endswith(key):
            yield os.path.split(file)[-1]


def _get_files(filepath):
    for file in os.listdir(filepath):
        file = os.path.join(filepath, file)
        if os.path.isdir(file):
            yield from _get_files(file)
        else:
            yield os.path.split(file)[-1]


def get_files(filepath, project="All"):
    """递归获取所有文件名"""
    result = list()
    if project == "All":
        for path in os.listdir(filepath):
            path = os.path.join(filepath, path)
            if not os.path.isdir(path):
                continue
            result.append(tuple(_get_files(path)))
    else:
        result.append(tuple(_get_files(filepath)))
    return result