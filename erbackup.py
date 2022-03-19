import os, shutil, sys, time
import pickle
import json

# Global variables
# utility_name = 'erbackup'
# er_save_file_name = 'ER0000.sl2'
# compression_method = '.zip'
# STEAM_UUID = "76561198037994630"
g_desc_dict = None
backup_name = ''
reserved_names = ['_last_load_backup']

with open('config.json', 'r') as f:
	config = json.load(f)
	
	utility_name = config['utility_name']
	STEAM_UUID = config['steam_uuid']
	compression_method = config['compression_method']
	game_directory = config['game_directory']
	er_save_file_name = config['save_file_name']
	
# Directories
sl2_path = os.path.expandvars(game_directory + '\\' + STEAM_UUID + '\\' + er_save_file_name)
root_backup_folder = os.getcwd() + '\\Backups\\'


# Capture arguments
command = None
save = 'save'
load = 'load'
list = 'list'
commands = [save, load, list]
argc = len(sys.argv)
argv = sys.argv

# --- Functions --- #
def error_msg(m1, m2):
	print("[Backup Manager] ERROR:\t" + m1)
	print("\t" + m2)

def log(msg):
	print('[Backup Manager]', msg)

def warn(msg):
	print('[Backup Manager] WARNING:', msg)

def confirm_action(message):
	response = ''
	s = message + " (y/n): "
	while (response != 'y' and response != 'n'):
		response = input(s)
	if response == 'n':
		return False
	return True

def make_archive(source, destination):
        base = os.path.basename(destination)
        name = base.split('.')[0]
        format = base.split('.')[1]
        archive_from = os.path.dirname(source)
        archive_to = os.path.basename(source.strip(os.sep))
        print(source, destination, archive_from, archive_to)
        shutil.make_archive(name, format, archive_from, archive_to)
        shutil.move('%s.%s'%(name,format), destination)

def save_description(name, description):
	path = root_backup_folder + '\\save_info.pkl'
	try:
		with open(path, 'rb') as handle:
			dict_desc = pickle.load(handle)
	except (IOError, EOFError) as e:
		# Create new dict
		dict_desc = {
		}
	finally:
		dict_desc[name] = description
		try:
			with open(path, 'wb') as handle:
				pickle.dump(dict_desc, handle, pickle.HIGHEST_PROTOCOL)
		except:
			pass
		return


def load_description(name):
	# Load the dictionary if it's not present in memory
	global g_desc_dict
	if g_desc_dict is None:
		try:
			with open(root_backup_folder + '\\save_info.pkl', 'rb') as handle:
				g_desc_dict = pickle.load(handle)
		except e:
			error_msg("Failed to load description file. Continuing without descriptions...")
			g_desc_dict = {}
	# Load the dictionary from global
	desc_dict = g_desc_dict

	# Trim the file extension
	name = name.replace(compression_method, '').strip()

	if name in desc_dict.keys():
		return desc_dict[name]
	# print("Failed to find", name, "in", desc_dict.keys())
	return ''

def print_save_details(name, stat, i):
	details = [('Description', load_description(name)), ('Last modified', time.ctime(stat.st_mtime))]
	print('-'*50)
	print("(" + str(i) + "): " + name + ":")

	for metric in details:
		print("\t" + metric[0] + ":", metric[1])

# ------------ #
# --- MAIN --- #
# ------------ #

# Clear the user's console
# clear = lambda: os.system('cls')
# clear()

if argc < 2:
	error_msg("Arguments required to use " + utility_name, "Syntax: erbackup [save | load | list] [backup_name]")
	sys.exit()

command = argv[1].lower()

if command not in commands:
	print("Command " + command + " not valid!")
	sys.exit()

if command == save:
	# Check for proper argument count
	if argc != 3:
		error_msg("Incorrect arguments to \'save\'",
		"Syntax: save {name of save}")
		sys.exit()

	# Obtain name argument
	backup_name = (argv[2]).strip()
	log("Attempting to save " + sl2_path + " to '" + backup_name + "'")
	# Check for non-reserved name
	if backup_name in reserved_names:
		error_msg(backup_name + ' is a reserved save name. Exiting...', '')
		sys.exit()
	
	# Check for existing backup
	path = os.path.join(root_backup_folder, backup_name)
	if os.path.isfile(path + compression_method):
		# Backup already exists, confirm overwrite
		warn("Backup '" + backup_name + "' already exists. Saving will overwrite this backup.")
		if not confirm_action("Are you sure you'd like to overwrite " + backup_name + "?"):
			log("Operation cancelled. Exiting.")
			sys.exit()

	# Prompt user description
	response = input("Enter save file description (press Enter to skip): ")
	description = response if len(response) > 0 else 'None'
	save_description(backup_name, description)

	# Perform backup
	print("Creating backup",backup_name,"in directory",root_backup_folder)
	try:
		os.mkdir(path)
	except:
		pass
	shutil.copy(sl2_path, path + '\\' + er_save_file_name)
	
	# Compress and remove original
	make_archive(path, root_backup_folder + '\\' + backup_name + compression_method)
	shutil.rmtree(path)
	print("Created backup.")
	
	# Exit program
	sys.exit()

if command == load:
	# Check for proper argument count
	if argc != 3:
		error_msg("Incorrect arguments to \'load\'",
		"Syntax: load {name of backup}")
		sys.exit()

	# Obtain name argument
	backup_name = (argv[2]).strip()
	log("Attempting to restore backup '" + backup_name + "'")
	path = os.path.join(root_backup_folder, backup_name + compression_method)
	if os.path.isfile(path):
		# Prompt user for confirmation
		# prompt
		
		# unzip archive
		shutil.unpack_archive(path, root_backup_folder)
		# move sl2 file to game directory
		log("Moving file...")
		os.replace(os.path.join(root_backup_folder, backup_name, er_save_file_name), sl2_path)
		log("Success! Moved backup '" + backup_name + "' to " + sl2_path)
		# clean up unzipped folder
		log("Cleaning up temporary directory...")
		shutil.rmtree(os.path.join(root_backup_folder, backup_name))
		log("Done.")
		
	else:
		# file does not exist, exit program
		error_msg("Backup '" + backup_name + "' does not exist.",
				  "Use '" + utility_name + " list' to see the current list of backups")
	sys.exit()


if command == list:
	i = 0
	print("Listing existing backups...")
	# Print all compressed save files since we use these as backups
	for save_file in (save_file for save_file in os.scandir(root_backup_folder) if save_file.is_file() and compression_method in save_file.name):
		i += 1
		print_save_details(save_file.name, os.stat(save_file.path), i)
	print('-'*50)
	print('Run the {load} {backup_name} command to load one of these backups.')
	print('Run the {remove} {backup_name} command to remove one of these backups.')
	sys.exit()
		