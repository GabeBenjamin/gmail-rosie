def handler(event, context):
    """
    The AWS Lambda handler that will be called

    :param event: AWS Lambda uses this parameter to pass in event data to the
    handler. This parameter is usually of the Python dict type. It can also be
    list, str, int, float, or NoneType type.
    :param context: AWS Lambda uses this parameter to provide runtime
    information to your handler. This parameter is of the LambdaContext type.
    """
    pass
def setUp():
    home_dir = os.path.dirname(os.path.realpath(__file__))
    label_id_pickle = os.path.join(home_dir, 'label_id_map.pickle')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
service = None
def getService():
    credentials = get_credentials()

    # Try and get labels to see if everything is working
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)


def cleanGmail():
    """

    :return:
    """

labelIdMap = {}
def getLabelIdsForLabels(labels):
    # Get all the labels since you can only get them by ids
    results = service.users().labels().list(userId='me').execute()
    allUserLabels = results.get('labels', [])

    for label in allUserLabels:
        labelName = label.get('name', '')
        if labelName in labels:
            labelIdMap[labelName] = label.get('id', None)

def getThreadsForLabels(labelIds):
    service.users().threads().list(userId='me', labelIds=[labelIds]).execute()
