#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: luzhiqi
# @Email: luzhiqi@ijunhai.com
# @Date: 2020-02-14 20:18:30
# @LastEditor: luzhiqi
# @LastEditTime: 2020-02-14 22:44:25

import os
import xlrd

from importlib import import_module


IMAGE_POSTFIX = ".png"

class ExcelParse:

    def __init__(self, excel):
        self.excel = self.get_true_name(excel)

    @staticmethod
    def get_true_name(excel):
        """检查excel的文件名及是否存在这个文件"""
        if not os.path.exists(excel):
            if excel.endswith("xls"):
                excel += "x"
            elif excel.endswith("xlsx"):
                excel = excel[:-1]
            else:
                pass
        return excel if os.path.exists(excel) else None

    def parse(self):
        """excel表的解析"""
        if not self.excel:
            return

        workbook = xlrd.open_workbook(self.excel, "a+")
        sheetname = workbook.sheet_names()[0]
        sheet = workbook.sheet_by_name(sheetname)
        result = list()
        # 第1行为标题行, 因此直接跳过从第2行开始
        for row in range(1, sheet.nrows):
            data = list()

            for value in sheet.row_values(row):
                if value == 0.0:
                    # 如果是0.0的float, 直接计成0
                    data.append(0)
                elif value:
                    # value要进行处理, 小写化, 整数化
                    value = value.lower() if isinstance(value, str) else int(value)
                    data.append(value)
                else:
                    pass

            # 未写.png后缀的需要加上后缀
            if data[0] == "click":
                if not data[1].endswith(IMAGE_POSTFIX):
                    data[1] += IMAGE_POSTFIX
            elif data[0] == "click_other":
                if isinstance(data[1], str) and not data[1].endswith(IMAGE_POSTFIX):
                    data[1] += IMAGE_POSTFIX
                if isinstance(data[2], str) and not data[2].endswith(IMAGE_POSTFIX):
                    data[2] += IMAGE_POSTFIX
            else:
                pass

            result.append(tuple(data))
        return result


def get_import_path(pyfile):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(path, pyfile.replace(path, "").replace("\\", ".")[1:-3])
    return pyfile.replace(path, "").replace("\\", ".")[1:-3]


def read_steps(filepath):
    """从filepath中获取到最后的stpes"""
    excel = None
    pyfile = None
    # 检索出对应的文件
    for file in os.listdir(filepath):
        file = os.path.join(filepath, file)
        if file.endswith(".xls") or file.endswith(".xlsx"):
            excel = file
        elif file.endswith(".py"):
            pyfile = file
    
    if excel and not pyfile:
        steps = ExcelParse(excel).parse()

    elif not excel and pyfile:
        # __import__引用会失败, 因此使用import_module
        steps = import_module(get_import_path(pyfile)).steps

    elif excel and pyfile:
        # 文件由测试人员上传, 因此直接用创建时间进行对比
        # 使用创建时间更大, 即创建时间更新的, 如果一样便用py文件
        if os.path.getctime(excel) > os.path.getctime(pyfile):
            steps = ExcelParse(excel).parse()
        else:
            steps = import_module(get_import_path(pyfile)).steps
            
    else:
        return "未找到步骤EXCEL表或PYTHON文件, 请重新上传或联系管理员查找原因!!!"
    message = "未能获取到行为列表,\n如果您上传的是PYTHON文件,\n请检查您的文件内容或联系管理员查找原因!!!"
    return steps if isinstance(steps, list) else message