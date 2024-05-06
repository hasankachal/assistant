import qdrant_client
# from langchain.vectorstores import Qdrant
from langchain.vectorstores import qdrant
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)
def document_loader(embeddings):
    doc_store = qdrant(
        client=client, collection_name="BBZR", 
        embeddings=embeddings,
    )

