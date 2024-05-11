from langchain_chroma import Chroma
from langchain_core.documents.base import Document
import pandas as pd

def document_loader(embeddings):
    filepath = "assets/framed_translate.csv"
    
    base_data = pd.read_csv(filepath,encoding="utf-8-sig")
    base_data.columns = [["id","parent","topic","page_content_en","page_content_fa"]]
    docs_buffer = []
    for _, chunk in base_data.iterrows():
        temp_doc = Document(page_content=f"{chunk['page_content_fa']} Topic={chunk['parent']}")
        # temp_doc = Document(page_content=f"topic={chunk['topic']} content={chunk['parent']}")
        temp_doc.metadata = {"source":filepath,"eng_content":chunk['page_content_en'],"topic": chunk["topic"],"parent":chunk['parent']}
        docs_buffer.append(temp_doc)
    vectorstore = Chroma.from_documents(documents=docs_buffer, embedding=embeddings)
    return vectorstore