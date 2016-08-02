#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Dropbox Directory Check Client.

This script checks files in a directory on Dropbox. If file does not exist in 
local directory, it will be downloaded. If file exists, it checkes hashes to 
determine that files are same or not. After download process ends, fetched file
is removed to trash directory on Dropbox.

Default arguments:
	accesstoken -	It is necessary to connect Dropbox App
			see https://www.dropbox.com/developers
	remotedir   -	Directory that you want to check in on Dropbox App
	remotetrash -	Trash directory to keep fetched files on Dropbox App
	localdir    -	Directory that you want to keep fetched files from Dropbox App

"""
import logging
import argparse
import dropbox
import sys
import traceback
import hashlib
from os import path, remove, mkdir
from shutil import copyfile

ACCESS_TOKEN = "@cc355t0k3n"
REMOTE_DIR = "/uploaded/"
REMOTE_TRASH = "/trash/"
LOCAL_DIR = "downloads/"

def checksum(localfile, otherfile):
	""" 
	return if files are same or not
	Compares hashes of two file-like objects 
	"""

	def gethash(file):
		hash_md5 = hashlib.md5()
		for chunk in iter(lambda: file.read(4096), b""):
			hash_md5.update(chunk)
		return hash_md5.hexdigest()
	localhash = gethash(localfile)
	otherhash = gethash(otherfile)

	if localhash == otherhash:
		return True
	return False

def init(token=ACCESS_TOKEN):
	""" 
	return dropbox.client.DropboxClient object
	Initializes connection between client and Dropbox
	"""

	try:
		logger.debug(
			'Connecting to Dropbox with access token: {0}'.format(
				token))
		client = dropbox.client.DropboxClient(token)
		check_result = client.account_info()
		logger.debug(check_result)
	except Exception:
		raise
	else:
		logger.debug('Connection has been established.')
		return client

def get_files_path(dbxclient, dirpath=REMOTE_DIR):
	""" 
	return file paths 
	Fetches contents of a directory on Dropbox
	"""

	logger.debug(
		'File paths are being fetched from \'{0}\'.'.format(
			dirpath))
	paths = []
	try:
		folder_metadata = dbxclient.metadata(dirpath)
		logger.debug(
			'Fetched metadata of directory: {0}'.format(
				folder_metadata))
		if folder_metadata['is_dir'] is False:
			raise Exception('REMOTE_DIR is not a directory path')
		paths = [file['path'] for file in folder_metadata['contents']]
	except:
		raise
	else:
		logger.debug(
			'Directory has {0} files.'.format(
				len(paths)))
		if len(paths) > 0:
			return paths
	return False

def fetch_file(dbxclient, path):
	""" Downloads a file as 'tmpfile' from Dropbox """

	logger.debug(
		'File from {0} is being fetched as \'tmpfile\'.'.format(
			path))
	result = None
	try:
		cache = open('tmpfile', 'wb')
		with dbxclient.get_file(path) as f:
		    cache.write(f.read())
	except:
		raise
	else:
		logger.debug(
			'File has been fetched.')
		cache.close()
		return True

def delete_file(dbxclient, filepath):
	""" Deletes a file from Dropbox """

	logger.debug(
		'{0} is being removed.'.format(
			filepath))
	try:
		dbxclient.file_delete(filepath)
	except:
		raise
	else:
		logger.debug('File has been removed.')
		return True

def move_to_trash(dbxclient, filepath, trashfolder=REMOTE_DIR):
	""" 
	If a file is fetched to local, 
	it is moved to trash on Dropbox
	"""

	logger.debug(
		'File from {0} is being moved to trash folder.'.format(
			filepath))
	filename = filepath.rsplit('/', 1)[-1]
	trashpath = ''.join((trashfolder, filename))
	try:
		dbxclient.file_move(filepath, trashpath)
	except dropbox.rest.ErrorResponse as err:
		if str(err).find('name already exists') >= 0:
			logger.debug(
				'A file with that name already exists at path '
				'\'{0}\''
				'It will be removed after delete that file'.format(
					trashpath))

			if delete_file(dbxclient, trashpath) is True:
				return move_to_trash(dbxclient, filepath, trashfolder)
		raise
	except:
		raise
	else:
		logger.debug('File has been moved to trash folder.')
		return True

def fetch_all(	dbxclient, 
				localfolder=LOCAL_DIR, 
				remotefolder= REMOTE_DIR, 
				trashfolder=REMOTE_TRASH):
	"""	Runs like main function. Checks and if necessary, 
		fetchs all files from Dropbox 
	"""
	try:
		paths = get_files_path(dbxclient, remotefolder)
		if paths is False:
			raise Exception('REMOTE_DIR is empty.')
		for p in paths:
			filename = p.rsplit('/', 1)[-1]
			localpath = ''.join((localfolder, filename))
			remotefile = fetch_file(dbxclient, p)
			if remotefile is not True:
				raise Exception(
					'There is something wrong with fetch_file().')
			if path.isdir(localfolder) is False:
				logger.debug(
					'Local folder \'{0}\' does not exist. '
					'Folder is being created.'.format(
						localfolder))
				mkdir(localfolder)
			if path.isfile(localpath) is True:
				with open(localpath, 'rb') as lf, open('tmpfile', 'rb') as rf:
					res = checksum(lf, rf)
				if res is True:
					logger.debug('Remote file is same with local file')
				elif res is False:
					logger.debug(
						'Remote file is different from local file. '
						'So, remote file is being overwritten to local file')
					copyfile('tmpfile', localpath)
			else:
				logger.debug(
						'Remote file is being copied to \'{0}\''.format(
							localpath))
				copyfile('tmpfile', localpath)
			move_to_trash(dbxclient, filepath=p, trashfolder=trashfolder)
	except:
		raise
	else:
		return True
	finally:
		if path.isfile('tmpfile') is True:
			remove('tmpfile')

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(
		description='Check Dropbox folder and '
		'fetch some files if there are uploaded ones recently.')

	parser.add_argument('-d', '--debug', dest='debug', action='store_true',
	                    help='debug mode, print console logs')

	parser.add_argument('--logfile', dest='logfile', action='store',
	                    default='checkdbxfiles.log', help='log file path')

	parser.add_argument('-a', '--accesstoken', dest='accesstoken', 
						action='store',
						help='Access token of Dropbox app')

	parser.add_argument('-r', '--remotedir', dest='remotedir', 
						action='store',
						help='Directory, that been checked files from, of Dropbox app')

	parser.add_argument('-t', '--remotetrash', dest='remotetrash', 
						action='store', 
						help='Trash folder of Dropbox app '
							'avoiding data loss')

	parser.add_argument('-l', '--localdir', dest='localdir', 
						action='store',
						help='Directory that keeps fetched files')

	args = parser.parse_args()

	ACCESS_TOKEN = ACCESS_TOKEN if args.accesstoken is None else args.accesstoken
	REMOTE_DIR = REMOTE_DIR if args.remotedir is None else args.remotedir
	REMOTE_TRASH = REMOTE_TRASH if args.remotetrash is None else args.remotetrash
	LOCAL_DIR = LOCAL_DIR if args.localdir is None else args.localdir
	
	#----------------------------LOGGING SETTINGS------------------------------

	logger = logging.getLogger('checkdbxfiles.log')
	logger.setLevel(logging.DEBUG)

	fh = logging.FileHandler(args.logfile)
	fh.setLevel(logging.DEBUG)

	ch = logging.StreamHandler()
	if args.debug:
		ch.setLevel(logging.DEBUG)
	else:
		ch.setLevel(logging.INFO)
	formatter = logging.Formatter(	'%(asctime)s - '
									'%(name)s - '
									'%(levelname)s - '
									'%(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)

	logger.addHandler(fh)
	logger.addHandler(ch)
	#--------------------------------------------------------------------------

	try:
		client = init(ACCESS_TOKEN)
		fetch_all(
			dbxclient=client,
			localfolder=LOCAL_DIR,
			remotefolder=REMOTE_DIR,
			trashfolder=REMOTE_TRASH)
	except Exception as err:
		if err.message == 'REMOTE_DIR is empty.':
			logger.warning(err)
			sys.exit(0)
		logger.error(traceback.format_exc())
		sys.exit(1)
	else:
		sys.exit(0)
