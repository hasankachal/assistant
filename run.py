from bb_assistant.util.logging import logger
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


from bb_assistant.util.translation import *
import streamlit as st
import time
from langchain_community.llms import Ollama
from bb_assistant.llm.poe import PoeApi,PoeRag
from bb_assistant.util.config import *
# from bb_assistant.llm import aya
from bb_assistant.vectorizer.e5 import E5Embeddings
from bb_assistant.retriever.chroma import document_loader
e5 = E5Embeddings()
wrapper = PoeApi(tokens=ACCOUNT_TOKENS2,headers=GLOBAL_HEADERS,proxy=HTTP_PROXY,cookies=ACCOUNT_TOKENS2)
docs = document_loader(embeddings=e5)
logger.info("Initiating LLM ...")
llm = PoeRag(wire=wrapper,retriever=docs)
if __name__ == "__main__":
    # translator()
    result,chatId = llm.invoke(chatbot="beaver",message="how much does the insurrance covers damages?")
    print(result,chatId)
