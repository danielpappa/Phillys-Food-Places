import pymongo
import Embedder
import json
import pandas
import os

class MongoManager:

    def __init__(self, mongo_uri):
        self.mongo_uri = mongo_uri

    def get_dataframe(self, dataframe):
        dataframe['review_embedding'] = dataframe["review_embedding"].apply(json.loads)
        return dataframe
    
    def get_mongo_client(self, mongo_uri):
        try:
            client = pymongo.MongoClient(mongo_uri)
            print("Connection to MongoDB successful")
            return client
        except pymongo.errors.ConnectionFailure as e:
            print(f"Connection failed: {e}")
            return None
        
    def set_mongo_db(self):

        if not self.mongo_uri:
            print("Mongo_uri missing or not set")

        mongo_client = self.get_mongo_client(self.mongo_uri)

        db = mongo_client["restaurants"]
        collection = db["philadelphia"]

        return collection

