# dropbox_scripts
Dropbox Directory Check Client
========
This script checks files in a directory on Dropbox. If file does not exist in 
local directory, it will be downloaded. If file exists, it checkes hashes to 
determine that files are same or not. After download process ends, fetched file
is removed to trash directory on Dropbox.

Default arguments:
``` shell
	accesstoken -	It is necessary to connect Dropbox App
					see https://www.dropbox.com/developers
	remotedir   -	Directory that you want to check in on Dropbox App
	remotetrash -	Trash directory to keep fetched files on Dropbox App
	localdir    -	Directory that you want to keep fetched files from Dropbox App
```
All options: 
``` shell
python checkdbxfiles.py [-h] [-d] [--logfile LOGFILE] [-a ACCESSTOKEN]
                        [-r REMOTEDIR] [-t REMOTETRASH] [-l LOCALDIR]
```
###Extra
I use this script for a project. Mostly, it is used as a deamon. It checks remote directory and triggers another one.

***
[Documentation Page](http://brsdurkut.github.io/CheckDropboxFiles/)
***
# DropboxUploader
Uploads a file or files in a directory. If you want to upload all files in a directory, add --folder flag. If you want to upload specific file paths, pass them directly. You can specify accesstoken, remotedir and localfolder in script.

Usage:
```shell
usage: dbxupload.py [-h] [-a ACCESSTOKEN] [-r REMOTEDIR] [-f]
                    paths [paths ...]
```
Example:
```shell
./dbxupload.py -a dropboxapp_accesstoken -r /test/ -f /localfolder/ # uploads files in directory
./dbxupload.py -a dropboxapp_accesstoken -r /test/ filepath ...     # uploads specified files
```
