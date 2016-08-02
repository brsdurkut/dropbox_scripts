#!/usr/bin/python
import logging
import dropbox
import argparse
import os, sys
import traceback

PATHS = []
ACCESS_TOKEN = "@cc355t0k3n"
REMOTE_DIR = "/uploaded/"
FOLDER = None

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

def upload(client, paths, remotedir=REMOTE_DIR):
	"""
	Uploads given files with full path
	"""
	success = []
	append = success.append
	for path in paths:
		if not os.path.isfile(path):
			continue
		try:
			filename = path.rsplit('/', 1)[-1]
			f = open(path, 'r')
			logger.debug(
				'{0} is being uploaded to {1}'.format(path, remotedir))
			client.put_file(
				'{0}{1}'.format(remotedir, filename),
				f,
				True)
			append(path)
		except Exception as err:
			raise
	return success

def paths_from_folder(folder):
	"""
	return filepaths in folder
	"""
	folder += '' if folder[-1] == '/' else '/'
	if not os.path.isdir(folder):
		raise Exception('Given path is not a directory!')
	try:
		filepaths = [''.join((folder, filename)) for filename in os.listdir(folder)]
		return filepaths
	except:
		raise


if __name__ == "__main__":

	parser = argparse.ArgumentParser(
		description='Uploads a file or files in a directory. '
		'If you want to upload all files in a directory, add --folder flag. '
		'If you want to upload specific file paths, pass them directly. '
		'You can specify accesstoken, remotedir and localfolder in script.\n'
		'Example:\n./dbxupload.py -a dropboxapp_accesstoken -r /test/ -f /localfolder/ '
		'or\n./dbxupload.py -a dropboxapp_accesstoken -r /test/ filepath ...',
		formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument(dest='paths', nargs='+', 
						help='Specified file paths to upload or folder')

	parser.add_argument('-a', '--accesstoken', dest='accesstoken', 
						action='store',
						help='Access token of Dropbox app')

	parser.add_argument('-r', '--remotedir', dest='remotedir', 
						action='store',
						help='Directory, that been uploaded files to, of Dropbox app')

	parser.add_argument('-f', '--folder', dest='folder', 
						action='store_true', default=False,
						help='Directory that you want to upload files')
	args = parser.parse_args()

	PATHS = args.paths
	ACCESS_TOKEN = args.accesstoken
	REMOTE_DIR = args.remotedir
	FOLDER = PATHS[0] if args.folder is True else None

	#----------------------------LOGGING SETTINGS------------------------------

	logger = logging.getLogger('dropboxuploader')
	logger.setLevel(logging.DEBUG)

	fh = logging.FileHandler('dropboxuploader.log')
	fh.setLevel(logging.DEBUG)

	ch = logging.StreamHandler()
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
		if FOLDER is None:
			filepaths = PATHS
		else:
			filepaths = paths_from_folder(FOLDER)
		client = init(ACCESS_TOKEN)
		success = upload(client, filepaths, REMOTE_DIR)
	except KeyboardInterrupt:
		loggler.info('Exiting..')
		sys.exit(0)
	except Exception as err:
		logger.error(traceback.format_exc())
		sys.exit(1)
	else:
		logger.info('Upload is successful for these files: {}'.format(success))
		sys.exit(0)