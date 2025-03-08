"""
Build file, used to make a new update-index file
"""

import os, sys
from update import md5_sum
from colour import *

from launcher import BUILD_VERSION

PATH = sys.path[0]

built_list = []
file_list = []
md5_list = []

for file in os.listdir(PATH):
	if (file != "build.py") and os.path.isfile(f"{PATH}/{file}"):
		file_list.append(file)

		md5_list.append(md5_sum(f"{PATH}/{file}"))

built_list.append(BUILD_VERSION)
built_list.append(file_list)
built_list.append(md5_list)

print(YELLOW + str(built_list) + RESET)