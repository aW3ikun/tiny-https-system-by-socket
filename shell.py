#!python3
# -*- coding: utf-8 -*-
# @Author: 虚伪
# @Date:   2019-12-29 22:13:47
# @Last Modified by:   虚伪
# @Last Modified time: 2019-12-30 03:00:10
import os
import time
try:
	os.popen("start cmd  /k py server.py")
	time.sleep(1)
	os.popen("start cmd /k py client.py")
except Exception:
	print("error")