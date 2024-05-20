
import json
from langchain_core.retrievers import BaseRetriever
from typing import Any, Callable, Dict, Iterable, List, Optional,Union
from langchain_core.documents import Document
from bb_assistant.util.globals import *
from flashrank import Ranker, RerankRequest
import pandas as pd


def translate_prompt(prompt:str):
    from bb_assistant.llm import aya
    result = aya.Aya101LLM()._call(
        f"Translate the following text from perisan to english then summerize it to usefull sentences: \n {prompt}"
    )
    print("TRANSLATED PROMPT :",result)
    return result

def translate_result(prompt: str):
    from bb_assistant.llm import aya
    prompt.replace(":"," ")
    return aya.Aya101LLM()._call(
        f"Translate the following text from English to Persian: {prompt}"
    )

def read_data(name):
    with open(f"assets/{name}","r",encoding='utf-8') as file:
        content = json.load(file)
    return content

def create_docs_old(raw:bool=True):
    filepath = "assets/fa.json"
    if raw:
        base_data = read_data("fa.json")
        docs_buffer = []
        for chunk in base_data:
            temp_doc = Document(page_content=chunk['content'].replace("\n","").replace('\u200c', ""))
            temp_doc.metadata = {"source":filepath,"id":chunk['id']}
            docs_buffer.append(temp_doc)
    else:
        core_path = "assets/framed_translate.csv"
        base_data = pd.read_csv(core_path,encoding="utf-8-sig")
        docs = read_data("fa.json")
        base_data.columns = ["id","parent","topic","page_content_en","page_content_fa"]
        docs_buffer = []
        for _, chunk in base_data.iterrows():
            print(len(docs))
            chunk["id"] = chunk["id"][2:-3]
            for idx,i in enumerate(docs):
                if i["id"] == chunk["id"]:
                    chunk["page_content"] = i["content"]
                    if chunk['topic'] != chunk['parent']:
                        ctx = f"{chunk['topic']} | {chunk['parent']}"
                    else:
                        txt = chunk["page_content"].split(".")[:2]
                        ctx = f"{chunk['topic']} | {txt}"
                    temp_doc = Document(page_content=ctx)
                    temp_doc.metadata = {"content":chunk["page_content"],"id": chunk["id"]}
                    docs_buffer.append(temp_doc)
                    docs.pop(idx)
    return docs_buffer
def create_docs(raw:bool=True):
    filepath = "assets/fa.json"
    if raw:
        core_path = "assets/framed.csv"
        base_data = pd.read_csv(core_path,encoding="utf-8-sig")
        docs_buffer = []
        for _, chunk in base_data.iterrows():
            if isinstance(chunk["page_content"],str):
                content = chunk["page_content"].replace("u200b","").replace("u200f","").replace("u200c","").replace("u200e","").replace("u200d","")
                temp_doc = Document(page_content=content)
                docs_buffer.append(temp_doc)
    else:
        core_path = "assets/framed.csv"
        base_data = pd.read_csv(core_path,encoding="utf-8-sig")
        docs_buffer = []
        for _, chunk in base_data.iterrows():
            if isinstance(chunk["page_content"],str):
                content = chunk["page_content"].replace("u200b","").replace("u200f","").replace("u200c","").replace("u200e","").replace("u200d","")
                if chunk['topic'] != chunk['parent'] and isinstance(chunk['parent'],str):
                    ctx = f"{chunk['topic']} | {chunk['parent']}"
                else:
                    txt = chunk["page_content"].split(".")[:2]
                    ctx = f"{chunk['topic']} | {txt}"
                temp_doc = Document(page_content=ctx.replace("u200b","").replace("u200f","").replace("u200c","").replace("u200e","").replace("u200d",""))
                temp_doc.metadata = {"content":content,"id": chunk["id"]}
                docs_buffer.append(temp_doc)
    return docs_buffer

ms = "ms-marco-MultiBERT-L-12"
zf = "rank_zephyr_7b_v1_full"
class Reranker:
    def __init__(
        self, model_name: str = ms, cache_dir: str = "assets/cache/"
    ) -> None:
        self.ranker = None
        self.model_name = model_name
        self.cache_dir = cache_dir

    def load(self):
        if self.ranker is None:
            self.ranker = Ranker(model_name=self.model_name, cache_dir=self.cache_dir, max_length=59000)

    def rerank(
        self,
        question: str,
        retrieved_documents: List[Document],
        top_k: Union[int, None] = None,
    ) -> List[Document]:

        self.load()

        formatted_documents_for_reranking = [
            {"id": i, "text": x.page_content, "meta": x.metadata}
            for i, x in enumerate(retrieved_documents)
        ]

        rerankrequest = RerankRequest(
            query=question, passages=formatted_documents_for_reranking
        )
        reranked_documents = self.ranker.rerank(rerankrequest)

        if top_k is None:
            top_k = len(reranked_documents)

        reranking_results = []
        for i in range(top_k):
            reranking_results.append(
                Document(page_content=reranked_documents[i]["text"])
            )
        return reranking_results
