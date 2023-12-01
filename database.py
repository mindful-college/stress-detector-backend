from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONNECTION_URI = os.getenv("DB_CONNECTION_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(DB_CONNECTION_URI, server_api=ServerApi('1'))
db = client[DB_NAME]
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

except Exception as e:
    print(e)
