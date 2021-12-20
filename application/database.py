import os
from pymongo import MongoClient
from flask_pymongo import PyMongo

mongo = PyMongo()

# MongoDB Setup
client = MongoClient(os.environ.get("MONGODB_URI"),
                     ssl=True, ssl_cert_reqs='CERT_NONE')
