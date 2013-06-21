import os
import urlparse

import pymongo


def get_connection():
    MONGO_URL = os.environ.get('MONGOHQ_URL')

    if MONGO_URL:
        # Get a connection
        conn = pymongo.Connection(MONGO_URL)
        # Get the database
        db = conn[urlparse(MONGO_URL).path[1:]]
    else:
        # Not on an app with the MongoHQ add-on, do some localhost action
        conn = pymongo.Connection('localhost', 27017)
        db = conn['agogo']
    return db
