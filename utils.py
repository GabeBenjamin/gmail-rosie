import os
import re
import pickle

import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from constants import APP_DIR
from constants import APPLICATION_NAME
from constants import CLIENT_SECRET_FILE
from constants import LABEL_REGEX
from constants import SCOPES

"""

from oauth2client.service_account import ServiceAccountCredentials

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CLIENT_SECRET_FILE, SCOPES)
"""

def getCredentials(flags=None):
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

def fetchLabelInfo(credentials, forceFetch=False):
    """

    :return:
    """
    labelMapFileName = os.path.join(APP_DIR, 'label-map.pickle')
    # Already have a label map saved
    if os.path.exists(labelMapFileName) and not forceFetch:
        return pickle.load(open(labelMapFileName, "rb" ))

    labelMap = {}
    # Try and get labels to see if everything is working
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().list(userId='me').execute()
    allUserLabels = results.get('labels', [])
    if not allUserLabels:
        print("Error - No labels found")
        return {}

    for label in allUserLabels:
        labelName = label.get('name', '').strip()
        if re.match(LABEL_REGEX, labelName):
            labelMap[labelName] = label.get('id', '')

    if not labelMap:
        print("ERROR - No labels found with the prefix {}".format(LABEL_REGEX))

    with open(labelMapFileName, 'w') as labelMapFile:
        pickle.dump(labelMap, labelMapFile)

    return labelMap

