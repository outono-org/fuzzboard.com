import os
from pymongo import MongoClient

# MongoDB Setup
client = MongoClient(os.environ.get("MONGODB_URI"),
                     ssl=True, ssl_cert_reqs='CERT_NONE')
