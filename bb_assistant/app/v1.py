from bb_assistant.util.logging import logger
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from bb_assistant.vectorizer.e5 import E5Embeddings
from bb_assistant.retriever.chroma import document_loader
from bb_assistant.util.globals import *
from bb_assistant.util.config import *
import streamlit as st
import time
from langchain_community.llms import Ollama
from bb_assistant.llm.poe import PoeApi,PoeRag
# from bb_assistant.llm import aya


st.set_page_config(layout='wide')


st.title('🦜🔗 BB-Assistant')
st.session_state.theme = "dark"

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


if "chat_history" not in st.session_state:
    logger.info("Initiating chat-history")
    st.session_state.chat_history = []
if "wrapper" not in st.session_state:
    st.session_state.wrapper = PoeApi(tokens=ACCOUNT_TOKENS2,headers=GLOBAL_HEADERS,proxy=HTTP_PROXY,cookies=ACCOUNT_TOKENS2)
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None
if "e5" not in st.session_state:
    logger.info("Initiating Vectorizer ...")
    st.session_state.e5 = E5Embeddings()
if "retriever" not in st.session_state:
    logger.info("Initiating retriever ...")
    st.session_state.retriever = document_loader(st.session_state.e5)
if "llm" not in st.session_state:
    logger.info("Initiating LLM ...")
    st.session_state.llm = Ollama(model="llama3")
for message in st.session_state.chat_history:
    if message["src"] == "Human":
        with st.chat_message("Human"):
            st.markdown(message["text"])
    elif message["src"] == "AI":
        with st.chat_message("AI"):
            st.markdown(message["text"])
def generate_response_llm(input_text,session):
    logger.info("Invoking prompt to chain ...")
    response,chatId = st.session_state.llm.invoke(chatbot="beaver",chatId=st.session_state.chat_id,message=input_text)
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

