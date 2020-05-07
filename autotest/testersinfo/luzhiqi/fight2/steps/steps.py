#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: luzhiqi
# @Email: luzhiqi@ijunhai.com
# @Date: 2020-01-8 15:18:56
# @LastEditor: luzhiqi
# @LastEditTime: 2020-02-21 17:42:04



steps = [
    # (操作, png文件, 是否需要一直等待(0是1否), 失败重试次数)
    ("click", "一键注册.png", 0, 3),
    ("click", "确定注册.png", 0, 3),
    ("click", "公告确定.png", 1, 0),
    ("click", "登录游戏.png", 0, 3),
    ("click", "随机名字.png", 0, 0),
    ("click", "随机名字.png", 1, 0),
    ("click", "随机名字.png", 1, 0),
    ("click", "创建角色.png", 0, 3),
    ("click", "随机名字.png", 1, 0),
    ("click", "创建角色.png", 1, 0),
    ("record_level", "1"),
    # (操作, png文件A, png文件B, 是否需要一直等待, 失败重试次数)
    # 第一个强制引导
    ("click_diff", "新手引导NPC.png", "技能图标.png",0, 3),
    ("click_diff", "新手引导NPC.png", "初始技能.png", 0, 3),
    ("click", "学习按钮.png", 0, 3),
    ("record_level", "4"),
    ("click", "查看图标.png", 0, 0),
    ("click", "退出强化.png", 0, 0),
    ("click", "穿戴按钮.png", 0, 1),
    ("click", "穿戴按钮.png", 0, 1),
    # 第二个强制引导
    ("click_diff", "新手引导NPC.png", "首领图标.png", 0, 3),
    ("click_diff", "新手引导NPC.png", "挑战按钮.png", 0, 3),
    ("record_level", "10"),
    ("click", "穿戴按钮.png", 1, 3),
    ("click", "穿戴按钮.png", 1, 3),
    ("click", "穿戴按钮.png", 1, 3),
    ("click", "穿戴按钮.png", 1, 3),
    ("click", "使用按钮.png", 0, 0),
    ("click", "使用按钮.png", 1, 0),
    ("click", "退出强化.png", 0, 0),

    ("click_diff", "新手引导NPC.png", "背包图标.png", 0, 3),
    ("click", "刀魅武器.png", 1, 2),
    ("click", "龙枪武器.png", 1, 2),
    ("click", "法尊武器.png", 1, 2),
    ("click", "退出背包.png", 0, 1),

    ("click", "查看按钮.png", 0, 1),
    ("click", "退出强化.png", 0, 1),

    ("click", "穿戴按钮.png", 1, 3),
    ("click", "查看按钮.png", 0, 1),
    ("click", "穿戴按钮2.png", 0, 1),
    ("click", "退出背包.png", 0, 1),

    ("click", "穿戴按钮.png", 1, 0),
    ("click", "查看按钮.png", 1, 0),
    ("click", "穿戴按钮2.png", 1, 0),
    ("click", "退出背包.png", 1, 0),

    ("click", "穿戴按钮.png", 1, 0),
    ("click", "查看按钮.png", 1, 0),
    ("click", "穿戴按钮2.png", 1, 0),
    ("click", "退出背包.png", 1, 0),

    ("click", "穿戴按钮.png", 1, 0),
    ("click", "查看按钮.png", 1, 0),
    ("click", "穿戴按钮2.png", 1, 0),
    ("click", "退出背包.png", 1, 0),
    # 第三个强制引导
    ("click", "锻造图标.png", 0, 3),
    ("click", "锻造图标.png", 1, 0),
    ("click", "锻造图标.png", 1, 0),
    ("click", "锻造图标.png", 1, 0),
    ("click", "锻造图标.png", 1, 0),
    ("click", "锻造图标.png", 1, 0),
    ("click", "头盔装备.png", 0, 3),
    ("click", "强化按钮.png", 0, 3),
    ("click", "强化按钮.png", 0, 3),
    ("click", "退出强化.png", 0, 3),
    ("record_level", "21"),
    # 第四个强制引导
    ("click_diff", "新手引导NPC.png", "首领图标.png", 0, 3),
    ("click_diff", "新手引导NPC.png", "挑战按钮.png", 0, 3),
    ("record_level", "22"),
    ("click", "穿戴按钮.png", 1, 3),
    ("click", "穿戴按钮.png", 1, 3),
    ("click", "穿戴按钮.png", 1, 3),
    ("click", "查看按钮.png", 1, 0),
    ("click", "穿戴按钮2.png", 1, 0),
    ("click", "退出背包.png", 1, 0),
    ("click", "查看按钮.png", 1, 0),
    ("click", "穿戴按钮2.png", 1, 0),
    ("click", "退出背包.png", 1, 0),
    ("click", "穿戴按钮.png", 1, 3),
    ("click", "穿戴按钮.png", 1, 3),
    ("click", "穿戴按钮.png", 1, 3),
    ("click", "穿戴按钮.png", 1, 3),
    # 第五个强制引导
    ("click_diff", "新手引导NPC.png", "背包图标.png", 0, 3),
    ("click_diff", "新手引导NPC.png", "仙贝兑换.png", 0, 3),
    ("click_diff", "新手引导NPC.png", "最大按钮.png", 1, 3),
    ("click", "兑换按钮.png", 1, 3),
    ("click", "退出仙贝兑换.png", 0, 3),
    ("click", "退出背包.png", 0, 3),
    ("record_level", "28"),

    ("click_diff", "新手引导NPC.png", "首领图标.png", 0, 3),
    ("click_diff", "新手引导NPC.png", "挑战按钮.png", 0, 3),
    ("record_level", "30"),
]

