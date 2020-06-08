#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: luzhiqi
# @Email: luzhiqi@ijunhai.com
# @Date: 2020-02-09 17:51:50
# @LastEditor: luzhiqi
# @LastEditTime: 2020-02-09 17:51:50

from django.db import models

class User(models.Model):
    username = models.CharField(max_length=12, unique=True)
    password = models.CharField(max_length=18)
    lastlogindate = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.username