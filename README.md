# Elden Ring Save Manager
This is a command line utility that allows you to quickly create and restore backups of your Elden Ring save file. Backups are stored in zip files to cut down on file size.

## Requirements
* Python 3.8
* Windows 10 (7 is untested).

## Installation
First, create a manual backup of your ER0000.sl2 file and store it outside of the scope of this program (just in case).

Clone the repo to any folder and run **setup.bat**.
Read the descriptions in **config.json** and adjust the variables accordingly (notably *steam_uuid*).

## Usage
After adding your steam_uuid to **config.json**, run **start.bat** and use the following commands:
```python
# List all available backups
erbackup list

# Create / overwrite a backup.
erbackup save {backup_name}

# Load a backup
erbackup load {backup_name}

# Remove a backup (not implemented)
erbackup remove {backup_name}
```

## Contributing
Pull requests are welcome. For major changes, feel free to fork this yourself.

I don't have any unit tests for this program, so I recommend performing a manual backup of your save data before you make changes.

## License
[MIT](https://choosealicense.com/licenses/mit/)
