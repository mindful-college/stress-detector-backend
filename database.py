from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import redis
import certifi

load_dotenv()
ca = certifi.where()

DB_NAME = os.getenv("DB_NAME")
DB_USER_NAME = os.getenv("DB_USER_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
CLUSTER = os.getenv("CLUSTER")

DB_CONNECTION_URI = f'mongodb+srv://{DB_USER_NAME}:{DB_PASSWORD}@{CLUSTER}/?retryWrites=true&w=majority'
client = MongoClient(DB_CONNECTION_URI, server_api=ServerApi('1'), tlsCAFile=ca)
db = client[DB_NAME]

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

except Exception as e:
    print(e)
