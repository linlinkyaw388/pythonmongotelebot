from pymongo import MongoClient

import pymongo      #for ASCENDING / DESCENING
from pprint import pprint

from dotenv import load_dotenv
import os
from datetime import datetime,timezone

from bson import ObjectId

load_dotenv()


try:
    mongo_uri = os.getenv("MONGO_URI")

    #connect to MongoDB server
    client = MongoClient(mongo_uri)


    #select database and collection 
    db = client["mydatabase"]
    collection = db["employees"]

    #input document ID (string)
    doc_id = input("Enter ID to search : ").strip()
    new_name = input("Enter new name : ").strip()
    new_email = input("Enter new email : ").strip()

    try:
        #convert string to objcectID
        object_id = ObjectId(doc_id)
    except Exception:
        print("Invalid ID format - must be a valid objectID string.")
        client.close()
        exit()


    query_fifler = {"_id:":object_id}
    update_operation = {
        "$set":{
            "username":new_name,
            "email" :new_email
        }
    }

    #Get document by id
    result = collection.update_one(query_fifler,update_operation)

    if result.matched_count > 0:
        print(f"update successfully.Modified count : {result.modified_count}")
    else:
        print(f"No record found with that ID.")
    


    
except Exception as e:
    print("Conncetion failed : ",e)

finally:
    #close connection
    client.close()


#www.Mongodb.com > resources >docs > Mongodb driver > python > pymongo or "get started with Mongodb > getstarted > CRUD operation  synchronous