from typing import Any, List
from bb_assistant.util.globals import *



def document_loader(retriever:BaseRetriever,docs:List[Document]):
    bm25_retriever = retriever.from_documents(documents=docs)
    bm25_retriever.k = 8
    return bm25_retriever