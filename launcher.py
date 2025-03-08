"""
Itchable game launcher
"""

BUILD_VERSION = 1

import questionary, os, sys, time

from colour import *

try:
	import update as update_helper
	can_update = True

except:
	can_update = False
	# Prevent crashes from update_helper calls
	class update_helper:
		def update():
			# This is hardcoded because this is intended to act as a RECOVERY FEATURE
			NotImplemented
			


QUESTIONARY_STYLES = questionary.Style(
	[
		("unsupported", "fg:#ff0000"),
		("non_itch", "fg:#d1c62a"),
		("itch", "fg:#14e329"),
		("system", "fg:#9e35e8")
	]
)

"""
CONSTANTS. DO NOT TOUCH
"""
PATH = sys.path[0]
USERNAME = os.getlogin()
VALID_EXECUTABLES = ["sh", "exe"] # Executable formats, in order of priority

"""
USER-CONFIGURABLE CONSTANTS
"""

GAME_DIR = f"/home/{USERNAME}/Games/"

"""
VARIABLES
"""

detected_directories = [] # Contains directories found in %GAME_DIR%
itch_games =  {} # Games installed from itch
cust_games =  [] # Games not installed from itch
unsupported = [] # Games we cannot launch (web games, for example)

show_unsupported_only = False

degraded = False 

def reimport():
	global update_helper

	del update_helper
	import update as update_helper

def clear():
	if os.name != "NT": os.system("clear")
	else: os.system("cls")

def search_game_dir(reset_list:bool=False):
	""" Search %GAME_DIR% """

	global detected_directories, itch_games, cust_games, unsupported

	if reset_list:
		detected_directories = []
		itch_games = {}
		cust_games = []
		unsupported = []

	# Build initial list
	for entry in os.listdir(GAME_DIR):
		if os.path.isdir(GAME_DIR + entry): detected_directories.append(entry)

	if len(detected_directories) == 0: print(RED + "WARNING: No directories were detected! Halting!"); time.sleep(10); sys.exit(1)

	# Parse the directories and determine type

	for game_folder in detected_directories:
		if os.path.exists(GAME_DIR + game_folder + "/.itch"): itch_check_versions(game_folder, GAME_DIR + game_folder + "/")
		else:
			valid = False
			for file in os.listdir(GAME_DIR + game_folder):
				try:
					if str(file).split(".", maxsplit=1)[1] in VALID_EXECUTABLES: valid = True
					else: NotImplemented
				except: NotImplemented # No file extension, don't handle it because it's probably Wine being annoying

			if valid: cust_games.append(game_folder)
			else: unsupported.append(game_folder)

def itch_check_versions(game_name:str, game_path:str):
	""" Check what versions of a game are available """

	global detected_directories, itch_games, cust_games, unsupported

	versions = []

	for version in os.listdir(game_path):
		if not version == ".itch": versions.append(version)

	itch_games.update({game_name:versions})

def find_executable(launch_path):
	launch_file = None

	for extension in VALID_EXECUTABLES:
		if launch_file != None: continue

		for file in os.listdir(launch_path):
				try:
					if not os.path.isfile(launch_path + file): continue;
					if launch_file != None: continue

					if str(str(file).split(".", maxsplit=1)[1]) == str(extension): 
						launch_file = file

				except Exception as err: print(str(err))

		if not launch_file == None:
			return launch_file
				
		else:
			return -1

def launch_executable(launch_path):
	""" Determine executable type and determine best launch method """
	
	if ".sh" in launch_path or ".x86_64" in launch_path:
		# Linux native, launch directly
		
		if not os.access(launch_path, os.X_OK):
			print(RED + "File is not allowed to execute!" + RESET)
			
			if input(BLUE + "Would you like to make it executable? [Y/N] > ").lower() == "y":
				os.system(f"chmod +x {launch_path}")

				print(YELLOW + "File was made executable. Launching..." + RESET)
			
			else:
				print(YELLOW + "Attempting to launch anyways..." + RESET)

		os.system(launch_path)

	elif ".exe" in launch_path:
		# Windows executable, determine if Wine is needed

		if os.name != "NT":
			print(YELLOW + "Warning: launching using Wine's default prefix! Output will be messy" + DRIVES)
			os.system(f"wine {launch_path}")
			print(RESET)
	
	else:
		print(RED + "Unknown executable type. Attempting direct run..." + RESET)
		os.system(launch_path)

	time.sleep(5)

# Build iniital list of games
search_game_dir()

if __name__ == "__main__":
	while True:
		clear()
		# Main loop #
		# Build the main menu #

		# The main menu is rebuilt each loop, because it doesn't cost that much to iterate a list in memory
		# Note: this menu should remain static unless search_game_dir() is explicitly called
		# Scanning the disk for files is more expensive, so we avoid it unless requested (on launch or by user)
		menu_choices = []

		if not show_unsupported_only:
			for game in itch_games.keys():
				menu_choices.append(questionary.Choice(title=[("class:itch", game)]))

			for game in cust_games:
				menu_choices.append(questionary.Choice(title=[("class:non_itch", game)]))

		# Unsupported games aren't shown by default, but give a menu option if unsupported games are detected

		if len(unsupported) != 0: 
			if not show_unsupported_only: menu_choices.append(questionary.Choice(title=[("class:unsupported", "(System) Unsupported Games")]))
			
		if show_unsupported_only:
			if len(unsupported) != 0:
				for game in unsupported:
					print(YELLOW + "The following games were detected, but cannot be launched by Itchable:" + RESET)
					print(RED + game + RESET)
			else: print(YELLOW + "No unsupported games detected" + RESET)

			show_unsupported_only = False
			input(RED + "Press enter to continue" + RESET)
			clear()

		else:
			if can_update: menu_choices.append(questionary.Choice(title=[("class:system", "(Itchable) Check for Updates")]))
			else:            menu_choices.append(questionary.Choice(title=[("class:system", "(Itchable) Repair")]))
			menu_choices.append(questionary.Choice(title=[("class:system", "(System) Scan for changes")]))
			if degraded: menu_choices.append(questionary.Choice(title=[("class:system", "(System) Exit")]))

			if degraded: print(RED + "Critical issue detected! MD5 sum mismatch detected. Re-run updater!" + RESET)

			prompt = questionary.select("Select a game", menu_choices, style=QUESTIONARY_STYLES).ask()

			match prompt:
				case "(System) Unsupported Games":
					show_unsupported_only = True
					clear()

				case "(Itchable) Repair":
					os.system(f"cd {PATH} && curl -O \"https://raw.githubusercontent.com/psychon-night/itchable-launcher/refs/heads/main/update.py\"")

					try: del update_helper
					except: NotImplemented
					try: 
						try: import update as update_helper
						except: NotImplemented
						can_update = False

						print(YELLOW + "Updater installed! Restart Itchable to use update functionality" + RESET)
					
					except Exception as err:
						print(RED + f"Repair failed! {str(err)}")
						time.sleep(10)

				case "(Itchable) Check for Updates":
					clear()

					update_result = update_helper.update(BUILD_VERSION)

					match update_result:
						case -6: print(RED + "Update failed: Updater missing")
						case -5: print(RED + "Update failed: Got an unexpected HTTP code")
						case -2: print(RED + "Update failed: SHA mismatch! Retry!" + RESET)
						case -1: print(RED + "Update failed: Unknown error")
						case  0: print(SPECIALDRIVE + "Update complete! Changes will be applied on next launch" + RESET)
						case 10: print(YELLOW + "Already up-to-date" + RESET)
						case 20: print(MAGENTA + "Local version is newer than server's version" + RESET)
						case  _: print(YELLOW + "Got an unknown return code")

					time.sleep(10)

				case "(System) Scan for changes":
					clear()
					print(YELLOW + "Scanning for new or changed files..." + RESET)

					search_game_dir(True) # Re-scan the disk

				case "(System) Exit":
					sys.exit(0)

				case _:
					clear()

					# Determine launch type
					if prompt in itch_games:
						print(f"{YELLOW}Launching {MAGENTA}{prompt}{YELLOW}...{RESET}" )

						launch_path = GAME_DIR + prompt

						if os.path.exists(launch_path):
							if len(os.listdir(launch_path)) > 2:
								# Show a prompt screen
								clear()

								detected_versions:list = os.listdir(launch_path)
								try: detected_versions.remove(".itch")
								except: NotImplemented

								version = questionary.select("Select version", detected_versions).ask()

								launch_path = f"{launch_path}/{version}/"

								launch_file = find_executable(launch_path)

								if not launch_file == -1:
									launch_path = launch_path + launch_file

									print(f"{YELLOW}Found executable! Launching using {MAGENTA}{launch_path}{RESET}")

									launch_executable(launch_path)

								else:
									print(RED + "Failed to find valid executable! Aborting..." + RESET)
									time.sleep(5)

						
						
							else:
								# Launch the available version
								found_launchable = False

								for dir in os.listdir(launch_path):
									if dir != ".itch": 
										found_launchable = True

										launch_path = launch_path + f"/{dir}/"
										print(f"{YELLOW}Found game version: {MAGENTA}{dir}{YELLOW}, attempting launch...")
										print(f"{YELLOW}Current path is {MAGENTA}{launch_path}{RESET}")

								if not found_launchable:
									print(f"{RED}Couldn't find a version of {MAGENTA}{prompt}{RED} to launch!")
									time.sleep(5)

								else:
									# Find the executable #

									launch_file = find_executable(launch_path)

									if not launch_file == -1:
										launch_path = launch_path + launch_file

										print(f"{YELLOW}Found executable! Launching using {MAGENTA}{launch_path}{RESET}")

										launch_executable(launch_path)

									else:
										print(RED + "Failed to find valid executable! Aborting..." + RESET)
										time.sleep(5)

						else:
							print(RED + "WARNING: Directory has moved or been deleted!" + RESET)
							time.sleep(5)
							search_game_dir(True) # Force a rescan, since and invalid entry has been generated

					elif prompt in cust_games:
						print(f"{YELLOW}Launching {MAGENTA}{prompt}{YELLOW}...{RESET}")

						launch_path = GAME_DIR + prompt + "/"
						launch_file = find_executable(launch_path)

						if not launch_file == -1:
							launch_path = launch_path + launch_file

							print(f"{YELLOW}Found executable! Launching using {MAGENTA}{launch_path}{RESET}")

							launch_executable(launch_path)

						else:
							print(RED + "Failed to find valid executable! Aborting..." + RESET)
							time.sleep(5)