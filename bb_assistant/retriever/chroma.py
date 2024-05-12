from langchain_chroma import Chroma
from bb_assistant.util.globals import *

def document_loader(retriever:BaseRetriever,docs:List[Document]):
    vectorstore = Chroma.from_documents(documents=docs, embedding=retriever).as_retriever({"k":15})
    return vectorstore