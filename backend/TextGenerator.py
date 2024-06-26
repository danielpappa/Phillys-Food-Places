from transformers import AutoTokenizer, AutoModelForCausalLM
import backend.MongoManager as MM
import os
import pandas as pd
from datasets import load_dataset

class TextGenerator:

    def __init__(self, pretrained, dataset):
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained)
        self.model = AutoModelForCausalLM.from_pretrained(pretrained) # for Gpu: , device_map = 'auto')
        self.mongo_manager = MM.MongoManager(os.getenv('MONGO_URI'))
        self.dataset = dataset
        self.collection = self.setup_collection()
    
    def setup_collection(self):

        df = load_dataset(self.dataset)
        df = pd.DataFrame(df["train"])
        df = df.drop(columns=["Unnamed: 0"])

        df = self.mongo_manager.get_dataframe(df)
        collection = self.mongo_manager.set_mongo_db(df)

        return collection

    def get_search_info(self, query):

        information = self.mongo_manager.vector_search(query, self.collection)

        search_info = ""

        for info in information:
            search_info += f"- Name: {info.get('name', 'N/A')}, Review: {info.get('text', 'N/A')} (Stars: {info.get('stars', 'N/A')})\n"

        if search_info == "":
            search_info = "Something went wrong and I could not access the provided data. Sorry I am unable to answer."

        return search_info
    
    def generate_response(self, query, history):
        sources = self.get_search_info(query)
        rag_padding = (
            f"Query: {query}\n\nI'm answering based on the following potential matches:\n\n{sources}\n\nLLM:"
        )
        input_ids = self.tokenizer(rag_padding, return_tensors="pt") #if Gpu: .to("cuda")
        response = self.model.generate(**input_ids, max_new_tokens=500)
        rag_text = self.tokenizer.decode(response[0]).split("LLM:")[-1]
        return rag_text.split("<eos>")[0]