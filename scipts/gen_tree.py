# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/2/11 22:41
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmai.com
# ------------------------------------
from pprint import pprint

case = [
	(1, 2, 3, 4),
	(1, 2, 4, 3),
	(2, 1, 3, 4),
	(2, 3, 1, 4),
	(3, 1, 2, 4)
]

result = {
	1:{
		2:{
			3:{
				4:{}
			},
			4:{
				3:{}
			}
		}
	},
	2:{
		1:{
			3:{
				4:{}
			}
		},
		3:{
			1:{
				4:{}
			}
		}
	},
	3:{
		1:{
			2:{
				4:{}
			}
		}
	}
}


def add_param_tuple_list(param_tuple_list: list):

	def add_param_tuple(raw_dict: dict, *param_tuple):

		def add_param(cur_dict: dict, cur_param):
			if not cur_dict.get(cur_param):
				cur_dict[cur_param] = dict()
			return cur_dict[cur_param]

		cur_dict = raw_dict
		for param in param_tuple:
			cur_dict = add_param(cur_dict, param)
		return raw_dict

	start_dict = dict()
	for param_tuple in param_tuple_list:
		add_param_tuple(start_dict, *param_tuple)
	return start_dict

case_result = add_param_tuple_list(case)
assert case_result == result

import re
re.sub()