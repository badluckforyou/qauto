import os
import csv


__all__ = ('parse_csv')


def check_file(file):
    if not file.endswith(".csv") or not os.path.exists(file):
        file = None
    return file


def parse_csv(file, keyline=None):
    """
    解析csv文件
    file: 文件名
    keyline: 如果传入了keylin, 
             则会打包成list(dict)形式, 
             并以keyline行的值为dict的key
    """
    # 如果为None就直接返回
    if check_file(file) is None:
        return
    result = list()
    with open(file, "r+") as f:
        reader = csv.reader(f)
        for line in reader:
            if not line:
                continue
            # keyline解析后的结果为dict
            if keyline is not None:
                if line == reader[keyline]:
                    continue
                data = dict()
                for i in range(len(line)):
                    data.setdefault(reader[keyline][i], line[i])
            else:
                data = tuple(line)
            result.append(data)
    return result