"""
Itchable Launcher Updater

Update proceedure:

1. Download /-update-index
2. Parse update-index:
	Structure:
		[version_id, [file1, file2, file3, so-on-and-so-forth], [shaSum1, shaSum2, shaSum3, so-on-and-so-forth]]

"""

import os, requests, sys, hashlib, json, time
from colour import *

### Configuration ###
PATH = sys.path[0]
ROOT_URL = "https://raw.githubusercontent.com/psychon-night/itchable-launcher/refs/heads/main" # Web link to the RAW GitHub files

def md5_sum(file:str):
	with open(file, 'rb', buffering=0) as disk_file:
		return hashlib.file_digest(disk_file, 'md5').hexdigest()

def update(current_version_id:int):
	""" Update Itchable.
	 
	Return values:
	- `-5 `: Aborted (wrong HTTP response)
	- `-2` : Aborted (SHA mismatch)
	- `-1` : Aborted (unknown error)
	- `0`: Success
	- `10`: No action required (up to date)
	- `20`: Time travel detected (newer local version)
	"""

	_prerun()

	print(YELLOW + "Checking for updates...")

	update_index_file = requests.get(ROOT_URL + "/update-index")
	http_response = update_index_file.status_code

	if http_response != 200:
		print(RED + f"Got HTTP {http_response}!" + RESET)

		cont = input("Continue anyways? [Y/N] > ").lower()

		abort = True if cont != "y" else False

	else: abort = False

	if not abort:
		try:
			update_index = json.loads(update_index_file.text)
		except:
			return -5

		if current_version_id < update_index[0]:
			print(YELLOW + "Update available! Working..." + RESET)

			for file in update_index[1]:
				os.system(f"cd {PATH} && curl -O \"{ROOT_URL}/{file}\" --clobber")

			for file in update_index[1]:
				local_hash = md5_sum(PATH + file)

		elif current_version_id == update_index[0]:
			return 10

		elif current_version_id > update_index[0]:
			return 20

		else:
			return -1


	else:
		print(RED + "Aborting!" + RESET)

		_postrun()

		time.sleep(5)

		return -5

def _prerun():
	""" INTERNAL function to get ready for downloads """
	if os.path.exists(PATH + "/.cache"):
		os.remove(PATH + "/.cache")

	os.mkdir(PATH + "/.cache")

def _postrun():
	""" Delete cache directory  """
	if os.path.exists(PATH + "/.cache"):
		os.remove(PATH + "/.cache")