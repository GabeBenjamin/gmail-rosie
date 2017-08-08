from __future__ import print_function
import os
import subprocess
from zipfile import ZipFile

from oauth2client import tools

from constants import APP_DIR
from constants import CLIENT_SECRET_FILE
from utils import getCredentials
from utils import fetchLabelInfo


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    flags.noauth_local_webserver = True
except ImportError:
    flags = None

def fetchDependencies(forceInstall):
    """

    :return:
    """
    dependencies_dir = os.path.join(APP_DIR, 'dependencies')
    # Already have a dependencies folder
    if os.path.exists(dependencies_dir) and not forceInstall:
        return

    os.makedirs(dependencies_dir)
    subprocess.call(
        "pip install -r requirements.txt --target={} --ignore-installed".format(
            dependencies_dir)
            .split())

def createLambdaZip():
    """

    :return:
    """
    LAMBDA_PREFIX = ""
    with ZipFile("lambda_files" + '.zip', 'w') as zipFile:
        # Write credentials
        zipFile.write(
            os.path.join(APP_DIR, '.credentials/' 'gmail-python-credentials.json'),
            os.path.join(LAMBDA_PREFIX, '.credentials/', 'gmail-python-credentials.json'))
        zipFile.write(
            os.path.join(APP_DIR, CLIENT_SECRET_FILE),
            os.path.join(LAMBDA_PREFIX, CLIENT_SECRET_FILE))
        # Write label-map
        zipFile.write(
            os.path.join(APP_DIR, 'label-map.pickle'),
            os.path.join(LAMBDA_PREFIX, 'label-map.pickle'))
        # TEST DELETE ME
        zipFile.write(
            os.path.join(APP_DIR, 'lambda_handler.py'),
            os.path.join(LAMBDA_PREFIX, 'lambda_handler.py'))
        # Write rosie script
        zipFile.write(
            os.path.join(APP_DIR, 'rosie.py'),
            os.path.join(LAMBDA_PREFIX, 'rosie.py'))
        # Write constants
        zipFile.write(
            os.path.join(APP_DIR, 'constants.py'),
            os.path.join(LAMBDA_PREFIX, 'constants.py'))
        # Write utils
        zipFile.write(
            os.path.join(APP_DIR, 'utils.py'),
            os.path.join(LAMBDA_PREFIX, 'utils.py'))
        # Write dependencies
        dependencies_dir = os.path.join(APP_DIR, 'dependencies')
        for root, dirs, files in os.walk(dependencies_dir):
            path = os.path.relpath(root, dependencies_dir)
            # Write all dependencies to the home directory of the zip file
            for file in files:
                zipFile.write(os.path.join(root, file), os.path.join(LAMBDA_PREFIX, path, file))

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = getCredentials(flags)
    fetchLabelInfo(credentials, False) # TODO add flag to force re-download
    fetchDependencies(False) # TODO add flag to force re-download
    createLambdaZip()


if __name__ == '__main__':
    main()