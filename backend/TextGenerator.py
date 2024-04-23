from transformers import AutoTokenizer, AutoModelForCausalLM
import backend.MongoManager as MM
import os
import pandas as pd
from datasets import load_dataset

tokenizer = AutoTokenizer.from_pretrained('google/gemma-2b-it')
model = AutoModelForCausalLM.from_pretrained('google/gemma-2b-it') # for Gpu: , device_map = 'auto')

df = load_dataset("danielpappa/philly_restaurants")
df = pd.DataFrame(df["train"])
df = df.drop(columns=["Unnamed: 0"])
mongo_manager = MM(os.getenv('MONGO_URI'))
df = mongo_manager.update_dataframe(df)
collection = mongo_manager.set_mongo_db()
mongo_manager.update_collection(collection)

class TextGenerator:

    def __init__(self, collection):
        self.collection = collection
    
    def get_search_info(self, query):

        information = mongo_manager.vector_search(query, self.collection)

        search_info = ""

        for info in information:
            search_info += f"- Name: {info.get('name', 'N/A')}, Review: {info.get('text', 'N/A')} (Stars: {info.get('stars', 'N/A')})\n"

        if search_info == "":
            search_info = "Something went wrong and I could not access the provided data. Sorry I am unable to answer."

        return search_info
    
    def generate_response(self, query):
        sources = self.get_search_info(query)
        rag_padding = (
            f"Query: {query}\n\nI'm answering based on the following potential matches:\n\n{sources}\n\nLLM:"
        )
        input_ids = tokenizer(rag_padding, return_tensors="pt") #if Gpu: .to("cuda")
        response = model.generate(**input_ids, max_new_tokens=500)
        rag_text = tokenizer.decode(response[0]).split("LLM:")[-1]
        return rag_text.split("<eos>")[0]