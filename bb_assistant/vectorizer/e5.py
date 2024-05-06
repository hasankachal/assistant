
from torch import cuda, bfloat16
from typing import Any, Dict, Iterator, List, Mapping, Optional
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer


e5_checkpoint = "intfloat/multilingual-e5-large-instruct"

e5_model = SentenceTransformer(e5_checkpoint)
# e5_model.max_seq_length = 1000

class E5Embeddings(Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        global e5_model
        embeddings = e5_model.encode(
            texts, convert_to_tensor=True, normalize_embeddings=True
        )
        return [embedding.tolist() for embedding in embeddings]

    def embed_query(self, text: str) -> List[float]:
        task_description = (
            "Given a web search query, retrieve relevant passages that answer the query"
        )
        query = f"Instruct: {task_description}\nQuery: {text}"
        resp = self.embed_documents([query])[0]
        return resp