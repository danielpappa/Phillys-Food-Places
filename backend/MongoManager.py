import pymongo
import json
import backend.Embedder as embedder

class MongoManager:

    def __init__(self, mongo_uri):
        self.mongo_uri = mongo_uri

    def get_dataframe(self, dataframe):
        dataframe['review_embedding'] = dataframe["review_embedding"].apply(json.loads)
        return dataframe
    
    def get_mongo_client(self):
        try:
            client = pymongo.MongoClient(self.mongo_uri)
            print("Connection to MongoDB successful")
            return client
        except pymongo.errors.ConnectionFailure as e:
            print(f"Connection failed: {e}")
            return None
        
    def set_mongo_db(self, dataframe):

        if not self.mongo_uri:
            print("Mongo_uri missing or not set")

        mongo_client = self.get_mongo_client()

        db = mongo_client["restaurants"]
        collection = db["philadelphia"]

        collection.delete_many({})
        documents = dataframe.to_dict("records")
        collection.insert_many(documents)
        print("Insertion worked out")

        return collection

    def vector_search(self, query, collection):

        embedding = embedder.Embedder("thenlper/gte-large")

        query_embedding = embedding.get_embedding(query)

        if query_embedding is None:
            return "Invalid query or embedding generation failed"

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "index_food",
                    "queryVector": query_embedding,
                    "path": "review_embedding",
                    "numCandidates": 3000,
                    "limit": 10, 
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

        results = collection.aggregate(pipeline)
        return list(results)
