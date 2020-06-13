"""
project所用到的信息查询均在这里处理
"""
import time
import ujson as json
import traceback

from contextlib import suppress

from autotest.database import DataBaseManage


def select_column_names(database, table):
    # 获取table的各个列的列名
    names = database.select("information_schema.COLUMNS", "COLUMN_NAME", "table_name='%s'" % table)
    return [name[0] for name in names]


def select_subserver(**kwargs):
    database = DataBaseManage()
    return database.select("autotest_subserver", **kwargs)


def select_task(**kwargs):
    database = DataBaseManage()
    return database.select("autotest_task", **kwargs)


def select_uitestresult(**kwargs):
    database = DataBaseManage()
    return database.select("autotest_autouitestresult", **kwargs)


def select_log(**kwargs):
    """由于log要实时获取离记录时过去多久, 因此放在这里进行计算"""
    data = []
    ret = _select_data_from_table("autotest_log", **kwargs)
    for r in ret:
        recordtime = time.mktime(time.strptime(r["recordtime"], "%Y-%m-%d %H:%M"))
        now = time.time()
        m, s = divmod(now - recordtime, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d != 0:
            r["pasttime"] = "%s Days Ago" % int(d)
        if d == 0 and h != 0:
            r["pasttime"] = "%s Hours Ago" % int(h)
        else:
            r["pasttime"] = "%s Mins Ago" % int(m)
        data.append(r)
    return data


def _select_uitestresult(**kwargs):
    return _select_data_from_table("autotest_autouitestresult", **kwargs)


def _select_data_from_table(table, wants="*", condition=None):
    """
    查找表中的数据, 如果能用json解析, 则进行解
    """
    data = []
    database = DataBaseManage()
    result = database.select(table, wants=wants, condition=condition)
    if result:
        if wants == "*":
            column_names = select_column_names(database, table)
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
