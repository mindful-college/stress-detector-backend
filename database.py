from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import redis
import certifi

load_dotenv()
ca = certifi.where()

# DB_CONNECTION_URI = os.getenv("DB_CONNECTION_URI")
DB_NAME = os.getenv("DB_NAME")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
DB_USER_NAME = os.getenv("DB_USER_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
CLUSTER = os.getenv("CLUSTER")

DB_CONNECTION_URI = f'mongodb+srv://{DB_USER_NAME}:{DB_PASSWORD}@{CLUSTER}/?retryWrites=true&w=majority'
print(DB_CONNECTION_URI)
client = MongoClient(DB_CONNECTION_URI, server_api=ServerApi('1'), tlsCAFile=ca)
db = client[DB_NAME]
redis_client = redis.Redis(
  host=REDIS_HOST,
  port=REDIS_PORT,
  password=REDIS_PASSWORD)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

except Exception as e:
    print(e)
