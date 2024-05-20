from bb_assistant.util.logging import logger
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from bb_assistant.vectorizer.e5 import E5Retriever
from bb_assistant.vectorizer.bm25 import BM25Retriever
from bb_assistant.vectorizer.tfidf import TfIdfRetriever
from bb_assistant.retriever.manual import create_vec_store
from bb_assistant.util.globals import *
from bb_assistant.util.config import *
import streamlit as st
import time
# from langchain_community.llms import Ollama
from bb_assistant.llm.poe import PoeApi,PoeRag
# from bb_assistant.llm import aya


st.set_page_config(layout='wide')


st.title('🦜🔗 BB-Assistant')
st.session_state.theme = "dark"
st.session_state.bot = "beaver"

st.markdown(
    """
<style>
    stChatMessage{
        text-align: right;
        direction:rtl;

    }
    .st-emotion-cache-janbn0 {
        flex-direction: row-reverse;
    }
    .st-emotion-cache-4oy321{
        text-align: left;
    }
    textarea {
        font-size: 16px;
        text-align: right;
        direction:rtl;
    }
    p {
        text-align: right;
        direction:rtl;
    }
</style>
""",
    unsafe_allow_html=True,
)
def _save(name,buffer):
    with open(f"assets/test/{name}.json","w",encoding='utf-8') as file:
        json.dump(buffer,file,ensure_ascii=False,indent=4)

def retrieve_topic(retriever:BaseRetriever,query:str) -> List[Document]:
    buffer = []
    result = retriever.invoke(query)
    for doc in result:
        classname = retriever.__repr__()[:13]
        logger.info(f"appending from {classname} CLASS")
        try:
            for line in doc.metadata["content"].split("."):
                if line != "" and line != " ":
                    buffer.append(Document(page_content=line))
        except Exception as fail:
            logger.error(f"failed to collect contnet metadata {doc} {fail}")
    _save(name="topic",buffer=[x.page_content for x in buffer])
    return buffer

def retrieve_page_content(retriever:BaseRetriever,query:str) -> List[Document]:
    buffer = []
    result = retriever.invoke(query)
    for doc in result:
        classname = retriever.__repr__()[:13]
        logger.info(f"appending from {classname} CLASS")
        for line in doc.page_content.split("."):
            if line != "" and line != " ":
                line.replace("\u200c","").replace("u200f","")
                buffer.append(Document(page_content=line))
    _save(name="raw",buffer=[x.page_content for x in buffer])
    return buffer

    
    return buffer
if "e5" not in st.session_state:
    logger.info("Initiating E3Embeddings ...")
    st.session_state.e5 = E5Retriever
if "bm25" not in st.session_state:
    logger.info("Initiating Bm25Embeddings ...")
    st.session_state.bm25 = BM25Retriever
if "tfidf" not in st.session_state:
    logger.info("Initiating Bm25Embeddings ...")
    st.session_state.tfidf = TfIdfRetriever
if "wrapper" not in st.session_state:
    logger.info("Initiating Wrapper Wire ...")
    st.session_state.wrapper = PoeApi(tokens=ACCOUNT_TOKENS3,headers=GLOBAL_HEADERS,proxy=HTTP_PROXY,cookies=ACCOUNT_TOKENS3,chat_bot=st.session_state.bot)
if "chat_id" not in st.session_state:
    logger.info("Initiating ChatId ...")
    st.session_state.chat_id = None
if "docs_raw" not in st.session_state:
    logger.info("Initiating Docs ...")
    st.session_state.docs_raw = create_docs(raw=True)
if "docs_topic" not in st.session_state:
    logger.info("Initiating Docs ...")
    st.session_state.docs_topic = create_docs(raw=False)
if "vecstore_1" not in st.session_state or "vecstore_2" not in st.session_state:
    logger.info("Initiating retriever on page content...")
    st.session_state.vecstore_1 = create_vec_store(retriever=st.session_state.tfidf,docs=st.session_state.docs_raw)
    st.session_state.vecstore_2 = create_vec_store(retriever=st.session_state.e5,docs=st.session_state.docs_topic)
if "llm" not in st.session_state:
    logger.info("Initiating LLM ...")
    st.session_state.llm = PoeRag(wire=st.session_state.wrapper)
if "chat_history" not in st.session_state:
    logger.info("Initiating chat-history")
    st.session_state.chat_history = []
# if "reranker" not in st.session_state:
#     logger.info("Initiating reranker ...")
#     st.session_state.reranker = Reranker()

def click_button():
    st.session_state.clear()

st.button("Reset", type="primary",on_click=click_button)
for message in st.session_state.chat_history:
    if message["src"] == "Human":
        with st.chat_message("Human"):
            st.markdown(message["text"])
    elif message["src"] == "AI":
        with st.chat_message("AI"):
            st.markdown(message["text"])
def generate_response_llm(input_text,session):
    logger.info("Invoking prompt to LLM ...")
    raw_context = retrieve_page_content(st.session_state.vecstore_1,input_text)[:9]
    topic_based_context = retrieve_topic(st.session_state.vecstore_2,input_text)[:9]
    
    raw_context.extend(topic_based_context)

    # ranked_context = st.session_state.reranker.rerank(input_text,context)
    _save(name="merged",buffer=[x.page_content for x in raw_context])
    response,chatId = st.session_state.llm.invoke(chatbot=st.session_state.bot,chatId=st.session_state.chat_id,message=input_text,context=raw_context)
    st.session_state.chat_id = chatId
    session.append({"src":"AI","text":response})
    for letter in response:
        time.sleep(0.01)
        yield letter



user_query = st.chat_input("Enter a prompt here")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append({"src":"Human","text":user_query})

    with st.chat_message("Human"):
        st.markdown(user_query,unsafe_allow_html=True)
    with st.chat_message("AI"):
        st.write_stream(generate_response_llm(user_query,st.session_state.chat_history))

