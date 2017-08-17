from datetime import datetime
import pickle
import os

from constants import LOG_DATE_STRING
from constants import ROSIE_LOG_DIR

SIMPLE_ROSIE_PREFIX = "simple_rosie_logger__"
SIMPLE_ROSIE_FILENAME = ROSIE_LOG_DIR + SIMPLE_ROSIE_PREFIX + LOG_DATE_STRING
class SimpleRosieLogger:
    """
    """

    def __init__(self):
        self.timestamp = datetime.now()
        self.emails = []


    def logEmail(self, emailObj):
        """

        :param emailObj:
        :return:
        """
        self.emails.append(emailObj)

    def save(self):
        """

        :return:
        """
        filename = self.timestamp.strftime(SIMPLE_ROSIE_FILENAME)

        # Make the log directory if it doesn't exist
        if not os.path.exists(ROSIE_LOG_DIR):
            os.makedirs(ROSIE_LOG_DIR)

        with open(filename, 'w') as f:
            blob = {
                'num_archived': len(self.emails),
                'emails': self.emails,
            }
            pickle.dump(blob, f)

    def load(self, date=None, dateString=None):
        """

        :return:
        """
        if date:
            filename = date.strftime(SIMPLE_ROSIE_FILENAME)
        elif dateString:
            filename = dateString
        else:
            # TODO
            filename = ""

        with open(filename, 'r') as f:
            blob = pickle.load(f)
            self.timestamp = blob.get('timestamp', date or datetime.now())
            self.emails = blob.get('emails', '')


