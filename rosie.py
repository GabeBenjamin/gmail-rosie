import httplib2
import logging
import re

from apiclient import discovery
from constants import LABEL_REGEX
from utils import getCredentials
from utils import fetchLabelInfo
from googleapiclient.http import BatchHttpRequest

from constants import INBOX_LABEL_NAME
from simple_rosie_logger import SimpleRosieLogger

#Turn off to do a full run
DEBUG = True
MAX_SIZE = 5
MAX_BATCH_SIZE = 100
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
rosieLogger = SimpleRosieLogger()
service = None
globalArchiveCounter = 0

def handler(event, context):
    """
    The AWS Lambda handler that will be called

    :param event: AWS Lambda uses this parameter to pass in event data to the
    handler. This parameter is usually of the Python dict type. It can also be
    list, str, int, float, or NoneType type.
    :param context: AWS Lambda uses this parameter to provide runtime
    information to your handler. This parameter is of the LambdaContext type.
    """
    credentials = getCredentials()
    getService(credentials)
    labelInfoMap = fetchLabelInfo(credentials)
    logger.debug("LabelInfo: {}".format(labelInfoMap))
    getThreadsForLabels(labelInfoMap)
    rosieLogger.save()
    logger.info(("*******************************\n"
                 "Archived Total of {} threads\n"
                 "*******************************").format(globalArchiveCounter))

def getService(credentials):
    global service
    # Try and get labels to see if everything is working
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

def getLabelIdsForLabels(labels):
    # Get all the labels since you can only get them by ids
    results = service.users().labels().list(userId='me').execute()
    allUserLabels = results.get('labels', [])

    for label in allUserLabels:
        labelName = label.get('name', '')
        if labelName in labels:
            labelIdMap[labelName] = label.get('id', None)

def threadCallback(id, response, exception):
    """

    :param id:
    :param response:
    :param exception:
    :return:
    """
    global globalArchiveCounter
    logger.debug("threadCallback:\nid: {}\nresponse: {}\nexception {}".format(id, response, exception))
    threadId = -1
    if response and not exception:
        threadId = response.get('id', -1)
    logger.info("{}: Archived thread {}".format(id, threadId))
    rosieLogger.logEmail(response)

    if exception:
        logger.error("Archiving thread failed: {}".format(exception))
    else:
        globalArchiveCounter += 1
        logger.info("Archived {} threads".format(globalArchiveCounter))

def threadsToArchiveCallback(id, response, exception):
    """

    :param id:
    :param response:
    :param exception:
    :return:
    """
    logger.debug("threadsToArchiveCallback:\nid: {}\nresponse: {}\nexception {}".format(id, response, exception))
    # No threads found
    if not response or 'resultSizeEstimate' not in response or response['resultSizeEstimate'] == 0 or 'threads' not in response:
        return

    counter = 0
    archiveBatch = BatchHttpRequest()
    for thread in response['threads']:
        logger.debug("Thread to archive: {}".format(thread))
        body = {
            "removeLabelIds": [
                INBOX_LABEL_NAME,
            ],
            "addLabelIds": [],
        }
        archiveBatch.add(service.users().threads().modify(userId='me', id=thread['id'], body=body), callback=threadCallback)
        counter += 1

        # Only do 1 run for debug instead of all
        if DEBUG:
            archiveBatch.execute()
            return

        if counter >= MAX_BATCH_SIZE:
            archiveBatch.execute()
            counter = 0
            archiveBatch = BatchHttpRequest()

    if counter > 0:
        archiveBatch.execute()

def getThreadsForLabels(labelIdMap):
    """

    :param labelIdMap:
    :return:
    """
    threadFetchBatch = BatchHttpRequest()
    for labelName, id in labelIdMap.iteritems():
        numDays = re.match(LABEL_REGEX, labelName).group(1)
        query = "label:{} older_than:{}d in:inbox".format(labelName, numDays)
        threadFetchBatch.add(service.users().threads().list(userId='me', q=query), callback=threadsToArchiveCallback)

    threadFetchBatch.execute()

if __name__ == '__main__':
    handler(None, None)
