# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/2/2 4:06
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------

import sys


def decorator(func, *args, **kwargs):
    def wrapper(*args, **kwargs):
        print("Starts decorating...")
        func(*args, **kwargs)
        print("Ended decorating !")

    return wrapper


class A:


    def __init__(self):
        print("this is A")

    @decorator
    def func_1(self, val):
        print(sys._getframe().f_code.co_name, val)


A().func_1()