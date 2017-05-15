from __future__ import print_function
import httplib2
import os
import re
import pickle
import subprocess
from zipfile import ZipFile

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from constants import LABEL_REGEX

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
APPLICATION_NAME = 'Gmail Rosie'
CLIENT_SECRET_FILE = 'client_secret.json'

VIRTUAL_ENV_HOME = os.environ['VIRTUAL_ENV']
APP_DIR = os.path.dirname(os.path.realpath(__file__))

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def getCredentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_dir = os.path.join(APP_DIR, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-credentials.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials

def fetchLabelInfo(credentials, forceFetch):
    """

    :return:
    """
    labelMapFileName = os.path.join(APP_DIR, 'label-map.pickle')
    # Already have a label map saved
    if os.path.exists(labelMapFileName) and not forceFetch:
        return

    labelMap = {}
    # Try and get labels to see if everything is working
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().list(userId='me').execute()
    allUserLabels = results.get('labels', [])
    if not allUserLabels:
        print("Error - No labels found")
        return

    for label in allUserLabels:
        labelName = label.get('name', '').strip()
        if re.match(LABEL_REGEX, labelName):
            labelMap[labelName] = label.get('id', '')

    if not labelMap:
        print("ERROR - No labels found with the prefix {}".format(LABEL_REGEX))

    with open(labelMapFileName, 'w') as labelMapFile:
        pickle.dump(labelMap, labelMapFile)

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
    LAMBDA_PREFIX = "rosie_package"
    with ZipFile(LAMBDA_PREFIX + '.zip', 'w') as zipFile:
        # Write label-map
        zipFile.write(
            os.path.join(APP_DIR, 'label-map.pickle'),
            os.path.join(LAMBDA_PREFIX, 'label-map.pickle'))
        # Write rosie script
        zipFile.write(
            os.path.join(APP_DIR, 'rosie.py'),
            os.path.join(LAMBDA_PREFIX, 'rosie.py'))
        # Write dependencies
        dependencies_dir = os.path.join(APP_DIR, 'dependencies')
        for root, dirs, files in os.walk(dependencies_dir):
            path = os.path.relpath(root, dependencies_dir)
            # Write all dependencies to the home directory of the zip file
            for file in files:
                zipFile.write(os.path.join(root, file), os.path.join(path, file))

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = getCredentials()
    fetchLabelInfo(credentials, False) # TODO add flag to force re-download
    fetchDependencies(False) # TODO add flag to force re-download
    createLambdaZip()


if __name__ == '__main__':
    main()