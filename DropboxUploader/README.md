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
