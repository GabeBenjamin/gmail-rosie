import os

# Regex
LABEL_REGEX = "^autoarchive-([0-9]+)$"

# File Paths
APP_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DATE_STRING = "%Y_%m_%d__%H_%M_%S.log"
ROSIE_LOG_DIR = "rosie_logs/"

# Gmail Auth
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
APPLICATION_NAME = 'Gmail Rosie'
CLIENT_SECRET_FILE = 'client_secret.json'

# Gmail Consts
INBOX_LABEL_NAME = 'INBOX'
