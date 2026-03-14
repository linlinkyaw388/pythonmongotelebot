from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()


# connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")


#connect to mongodb server
client = MongoClient(mongo_uri)

#seletct database
db = client["mydatabase"]



def dbconnect():
    return db