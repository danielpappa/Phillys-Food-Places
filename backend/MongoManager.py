import pymongo
import json
import backend.Embedder as embedder
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

    def vector_search(self, query):

        query_embedding = embedder.get_embedding(query)

        if query_embedding is None:
            return "Invalid query or embedding generation failed"

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "index_food",
                    "queryVector": query_embedding,
                    "path": "review_embedding",
                    "numCandidates": 150,
                    "limit": 5,  # Return top 2 matches
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": 1,
                    "stars": 1,
                    "text": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        results = self.set_mongo_db().aggregate(pipeline)
        return list(results)
