from bb_assistant.util.logging import logger
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from bb_assistant.vectorizer.e5 import E5Embeddings
from bb_assistant.vectorizer.bm25 import BM25Retriever
from bb_assistant.retriever.custom import document_loader as custom_retriever
from bb_assistant.retriever.chroma import document_loader as chroma_retriever
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

def retrieve_context(retrievers:BaseRetriever,query:str) -> List[Document]:
    buffer = []
    for retriever in retrievers:
        per_retriever = []
        result = retriever.invoke(query)
        for doc in result:
            classname = retriever.__repr__()[:15]
            logger.info(f"appending doc from {classname} CLASS")
            for line in doc.page_content.split("."):
                if line != "" and line != " ":
                    line.replace("\u200c","")
                    buffer.append(Document(line))
                    per_retriever.append(line)
        _save(name=classname,buffer=per_retriever)
    return buffer



if "e5" not in st.session_state:
    logger.info("Initiating E3Embeddings ...")
    st.session_state.e5 = E5Embeddings()
if "bm25" not in st.session_state:
    logger.info("Initiating Bm25Embeddings ...")
    st.session_state.bm25 = BM25Retriever
if "wrapper" not in st.session_state:
    logger.info("Initiating Wrapper Wire ...")
    st.session_state.wrapper = PoeApi(tokens=ACCOUNT_TOKENS2,headers=GLOBAL_HEADERS,proxy=HTTP_PROXY,cookies=ACCOUNT_TOKENS2)
if "chat_id" not in st.session_state:
    logger.info("Initiating ChatId ...")
    st.session_state.chat_id = None
if "docs" not in st.session_state:
    logger.info("Initiating Docs ...")
    st.session_state.docs = create_docs()
if "retriever_1" not in st.session_state:
    logger.info("Initiating retriever 1...")
    st.session_state.retriever_1 = custom_retriever(retriever=st.session_state.bm25,docs=st.session_state.docs)
if "retriever_2" not in st.session_state:
    logger.info("Initiating retriever 2 ...")
    st.session_state.retriever_2 = chroma_retriever(retriever=st.session_state.e5,docs=st.session_state.docs)
if "reranker" not in st.session_state:
    logger.info("Initiating reranker ...")
    st.session_state.reranker = Reranker()
if "llm" not in st.session_state:
    logger.info("Initiating LLM ...")
    st.session_state.llm = PoeRag(wire=st.session_state.wrapper)
if "chat_history" not in st.session_state:
    logger.info("Initiating chat-history")
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    if message["src"] == "Human":
        with st.chat_message("Human"):
            st.markdown(message["text"])
    elif message["src"] == "AI":
        with st.chat_message("AI"):
            st.markdown(message["text"])
def generate_response_llm(input_text,session):
    logger.info("Invoking prompt to LLM ...")
    context = retrieve_context([st.session_state.retriever_1,st.session_state.retriever_2],input_text)
    ranked_context = st.session_state.reranker.rerank(input_text,context)
    response,chatId = st.session_state.llm.invoke(chatbot=st.session_state.bot,chatId=st.session_state.chat_id,message=input_text,context=ranked_context)
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

