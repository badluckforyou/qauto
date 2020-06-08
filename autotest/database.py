import pymysql
import traceback

from qauto import settings


# db = {
#     "HOST": "127.0.0.1",
#     "PORT": 3306,
#     "USER": "root",
#     "PASSWORD": "0987abc123",
#     "DBNAME": "qauto"
# }

db = settings.DATABASES["default"]



def operas(func):
    def wrapper(self, *args, **kwargs):
        """
        先判定行为流程为(connect, func, close) or (func)
        如果传入的判定key与预期不符, 直接raise
        如果行为是前者, 在connect连接失败时, 直接返回False
        """
        if "connection" not in kwargs:
            kwargs["connection"] = True

        if kwargs["connection"] is True:
            try:
                self.connect()
            except ConnectionError:
                traceback.print_exc()
                # out有可能是None, 因此连接失败需要返回False
                return False
            kwargs.pop("connection")
            out = func(self, *args, **kwargs)
            self.close()
        elif kwargs["connection"] is False:
            kwargs.pop("connection")
            out = func(self, *args, **kwargs)
        else:
            raise ValueError("The value of 'connection' is not True or False, it's %s" % kwargs["connection"])
        return out
    return wrapper


class DataBaseManage:

    """
    除connect/colse外, 每一个行为都内置了默认执行过程为:connect, opera, close
    如果需要连接后执行多个行为, 需要传入connection=False
    """

    def __init__(self, database=None):
        self.database = database or db

    def connect(self):
        """连接数据库"""
        try:
            self.conn = pymysql.Connect(host=self.database["HOST"], 
                                        port=int(self.database["PORT"]),
                                        user=self.database["USER"], 
                                        passwd=self.database["PASSWORD"],
                                        db=self.database["NAME"], 
                                        charset="utf8", 
                                        autocommit=True)
        except:
            raise ConnectionError("Can't connect to MySQL server on '%s'" % self.database["HOST"])
        else:
            self.curs = self.conn.cursor()

    def close(self):
        """断开连接"""
        self.curs.close()
        self.conn.close()

    @operas
    def select(self, table, wants="*", keywords=None):
        """
        select xx from table where xx=xx;
        从表中获取对应的数据
        return [(,), (,)] or None
        """
        if keywords:
            statement = "SELECT {} FROM {} WHERE {};".format(wants, table, keywords)
        else:
            statement = "SELECT {} FROM {};".format(wants, table)
        out = self.curs.execute(statement)
        result = list(self.curs.fetchmany(out)) if out else None
        return result

    @operas
    def insert(self, table, data):
        """
        insert into table values xx=xx;
        将数据插入对应的表
        """
        statement = "INSERT INTO {} SET {};".format(table, data)
        self.curs.execute(statement)

    @operas
    def delete(self, table, keywords):
        """
        delete from table where xx=xx;
        在列表中删除行
        """
        statement = "DELETE FROM {} WHERE {};".format(table, keywords)
        self.curs.execute(statement)

    @operas
    def update(self, table, data, keywords):
        """
        update table set xx=xx where xx=xx;
        更新列表数据
        """
        statement = "UPDATE {} SET {} WHERE {};".format(table, data, keywords)
        self.curs.execute(statement)

dbmanage = DataBaseManage()