from langchain_chroma import Chroma
from bb_assistant.util.globals import *
import pandas as pd


# def topic_loader(retriever:BaseRetriever,docs:List[Document]):
#     filepath = "assets/framed_translate.csv"
#     base_data = pd.read_csv(filepath,encoding="utf-8-sig")
#     base_data.columns = ["id","parent","topic","page_content_en","page_content_fa"]
#     docs_buffer = []
#     for _, chunk in base_data.iterrows():
#         chunk["id"] = chunk["id"][2:-3]
#         for idx,i in enumerate(docs):
#             if i.metadata["id"] == chunk["id"]:
#                 chunk["page_content"] = i.page_content
#                 if chunk['topic'] != chunk['parent']:
#                     ctx = f"{chunk['topic']} | {chunk['parent']}"
#                 else:
#                     txt = chunk["page_content"].split(".")[:2]
#                     ctx = f"{chunk['topic']} | {txt}"
#                 temp_doc = Document(page_content=ctx)
#                 temp_doc.metadata = {"content":chunk["page_content"],"id": chunk["id"]}
#                 docs_buffer.append(temp_doc)
#                 docs.pop(idx)
#     print(f"LOADING {len(docs_buffer)}")
#     vectorstore = retriever.from_documents(documents=docs_buffer)
#     vectorstore.k = 10
#     return vectorstore

def create_vec_store(retriever:BaseRetriever,docs:List[Document]):
    bm25_retriever = retriever.from_documents(documents=docs)
    bm25_retriever.k = 10
    return bm25_retriever

