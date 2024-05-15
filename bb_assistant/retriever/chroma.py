from langchain_chroma import Chroma
from bb_assistant.util.globals import *
import pandas as pd
def document_loader2(retriever:BaseRetriever,docs:List[Document]):
    vectorstore = Chroma.from_documents(documents=docs, embedding=retriever).as_retriever(k=8)
    return vectorstore


def document_loader(retriever:BaseRetriever,docs:List[Document]):
    filepath = "assets/framed_translate.csv"
    base_data = pd.read_csv(filepath,encoding="utf-8-sig")
    base_data.columns = [["id","parent","topic","page_content_en","page_content_fa"]]
    docs_buffer = []
    for _, chunk in base_data.iterrows():
        # temp_doc = Document(page_content='\n'.join(chunk['page_content']))
        chunk["id"] = chunk["id"][2:-3]
        print(len(docs))
        for idx,i in enumerate(docs):
            if i.metadata["id"] == chunk["id"]:
                chunk["page_content"] = i.page_content
                temp_doc = Document(page_content=f"{chunk['topic']} -- {chunk['parent']} ")
                temp_doc.metadata = {"content":chunk["page_content"],"id": chunk["id"]}
                docs_buffer.append(temp_doc)
                docs.pop(idx)
    vectorstore = Chroma.from_documents(documents=docs_buffer, embedding=retriever).as_retriever(k=7)
    return vectorstore
