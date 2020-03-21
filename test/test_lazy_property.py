# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/3/10 23:31
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------

class lazy(object):
	def __init__(self, func):
		self.func = func

	def __get__(self, instance, cls):
		val = self.func(instance)
		setattr(instance, self.func.__name__, val)
		return val


class Circle(object):
	def __init__(self, radius):
		self.radius = radius

	@lazy
	def area(self):
		print("calculate area")
		return 3.14 * self.radius ** 2