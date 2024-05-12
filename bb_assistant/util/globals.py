
import json
from langchain_core.retrievers import BaseRetriever
from typing import Any, Callable, Dict, Iterable, List, Optional,Union
from langchain_core.documents import Document
from bb_assistant.util.globals import *
from flashrank import Ranker, RerankRequest



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

def create_docs():
    filepath = "assets/fa.json"
    base_data = read_data("fa.json")
    docs_buffer = []
    for chunk in base_data:
        temp_doc = Document(page_content=chunk['content'].replace("\n",""))
        temp_doc.metadata = {"source":filepath,"id":chunk['id']}
        docs_buffer.append(temp_doc)
    return docs_buffer


class Reranker:
    def __init__(
        self, model_name: str = "ms-marco-MultiBERT-L-12", cache_dir: str = "/home/frox/"
    ) -> None:
        self.ranker = None
        self.model_name = model_name
        self.cache_dir = cache_dir

    def load(self):
        if self.ranker is None:
            self.ranker = Ranker(model_name=self.model_name, cache_dir=self.cache_dir)

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
