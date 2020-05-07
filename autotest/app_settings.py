#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: luzhiqi
# @Email: luzhiqi@ijunhai.com
# @Date: 2020-02-09 18:25:47
# @LastEditor: luzhiqi
# @LastEditTime: 2020-02-14 22:44:41

import os

class AppSettings:

    IPS = {
        "121.37.191.34": [
            # cpu, yunphone ip number, yunphone ip, docker name, 
            (0, 0, "stress0:v0"),
            (1, 1, "stress1:v0"),
            (2, 2, "stress2:v0"),
            (3, 3, "stress3:v0"),
            (4, 4, "stress4:v0"),
            (5, 5, "stress5:v0"),
            (6, 6, "stress6:v0"),
            (7, 7, "stress7:v0"),
            (8, 8, "stress8:v0"),
            (9, 9, "stress9:v0")
        ],
        "121.37.164.177": [
            (0, 10, "stress10:v0"),
            (1, 11, "stress11:v0"),
            (2, 12, "stress12:v0"),
            (3, 13, "stress13:v0"),
            (4, 14, "stress14:v0"),
            (5, 15, "stress15:v0"),
            (6, 16, "stress16:v0"),
            (7, 17, "stress17:v0"),
            (8, 18, "stress18:v0"),
            (9, 19, "stress19:v0")
        ],
        "121.37.191.119": [
            (0, 20, "stress20:v0"),
            (1, 21, "stress21:v0"),
            (2, 22, "stress22:v0"),
            (3, 23, "stress23:v0"),
            (4, 24, "stress24:v0"),
            (5, 25, "stress25:v0"),
            (6, 26, "stress26:v0"),
            (7, 27, "stress27:v0"),
            (8, 28, "stress28:v0"),
            (9, 29, "stress29:v0")
        ],
        "121.37.160.63": [
            (0, 30, "stress30:v0"),
            (1, 31, "stress31:v0"),
            (2, 32, "stress32:v0"),
            (3, 33, "stress33:v0"),
            (4, 34, "stress34:v0"),
            (5, 35, "stress35:v0"),
            (6, 36, "stress36:v0"),
            (7, 37, "stress37:v0"),
            (8, 38, "stress38:v0"),
            (9, 39, "stress39:v0")
        ],
        "121.37.181.137": [
            (0, 40, "stress40:v0"),
            (1, 41, "stress41:v0"),
            (2, 42, "stress42:v0"),
            (3, 43, "stress43:v0"),
            (4, 44, "stress44:v0"),
            (5, 45, "stress45:v0"),
            (6, 46, "stress46:v0"),
            (7, 47, "stress47:v0"),
            (8, 48, "stress48:v0"),
            (9, 49, "stress49:v0")
        ]
    }
    TITLE = "AutoTestofGameQuality|v0.0.0beta"
    COMPANY = "君海游戏"
    PHONESNUMBER = 25
    GAMES = {
        "所有游戏": "",
        "战玲珑2": "fight2",
    }
    RESOLUTIONS = [
        "",
        "960 × 540",
        "1136 × 640",
        "1280 × 720",
        "1320 × 720",
        "1440 × 720",
        "1480 × 720",
        "1520 × 720",
        "1560 × 720",
        "1600 × 720",
        "1334 × 750",
        "1792 × 828",
        "1920 × 1080",
        "2160 × 1080",
        "2220 × 1080",
        "2244 × 1080",
        "2280 × 1080",
        "2310 × 1080",
        "2312 × 1080",
        "2340 × 1080",
        "2400 × 1080",
        "2436 × 1125",
        "1920 × 1125",
        "2400 × 1176",
        "1920 × 1200",
        "2688 × 1242",
        "2560 × 1312",
        "2560 × 1440",
        "2880 × 1440",
        "2960 × 1440",
        "3120 × 1440",
        "2048 × 1536",
        "2224 × 1668",
        "2388 × 1668",
        "2732 × 2048",
        "3840 × 2160",
    ]
    FILEPATH = os.path.dirname(os.path.abspath(__file__))
    TESTERFOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testersinfo")

