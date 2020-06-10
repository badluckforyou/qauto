##############################################
# 以下接口暂未被使用, 优先使用django自带的modles #
##############################################
import ujson as json

from contextlib import suppress

from database import dbmanage



RESULT_FORMAT = {
    "id": 0,

}

def select_column_names(table):
    names = dbmanage.select("information_schema.COLUMNS", "COLUMN_NAME", "table_name='%s'" % table)
    return [name[0] for name in names]

def select_subserver(**kwargs):
    return dbmanage.select("autotest_subserver", **kwargs)


def select_task(**kwargs):
    return dbmanage.select("autotest_task", **kwargs)


def select_uitestresult(**kwargs):
    table = "autotest_autouitestresult"
    return _select_uitestresult(table, **kwargs)


def _select_uitestresult(table, wants="*", keywords=None):
    """
    查找autouitest表中的数据, 如果能用json解析, 则进行解
    """
    data = []
    result = dbmanage.select(table, wants=wants, keywords=keywords)
    if result:
        if wants == "*":
            column_names = select_column_names(table)
        else:
            column_names = [w.strip() for w in wants.split(",")]
        for r in result:
            d = {}
            for i, v in enumerate(r):
                with suppress(Exception):
                    v = json.loads(v)
                d.setdefault(column_names[i], v)
            data.append(d)
    return data


def insert_uitestresult(data):
    table = "autotest_autouitestresult"
    d = ""
    for k, v in data.items():
        if isinstance(v, int) or isinstance(v, float):
            d += "%s=%s, " % (k, v)
        else:
            d += "%s=%s, " % (k, json.dumps(v))
    dbmanage.insert(table, d)
