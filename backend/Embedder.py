from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, embedding_model):
        self.embedding_model = SentenceTransformer(embedding_model)

    def get_embedding(self, text: str) -> list[float]:
        if not text:
            print("No text to be embedded")
            return []

        embedding = self.embedding_model.encode(text)
        return embedding.tolist()