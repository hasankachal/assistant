from bb_assistant.util.logging import logger
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from bb_assistant.vectorizer.e5 import E5Embeddings
from bb_assistant.retriever.chroma import document_loader
from bb_assistant.util.translation import *
import streamlit as st
import time
from langchain_community.llms import Ollama
from bb_assistant.llm import aya


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
if "llm" not in st.session_state:
    logger.info("Initiating LLM ...")
    st.session_state.llm = Ollama(model="llama3")
if "e5" not in st.session_state:
    logger.info("Initiating Vectorizer ...")
    st.session_state.e5 = E5Embeddings()
if "retriever" not in st.session_state:
    logger.info("Initiating retriever ...")
    st.session_state.retriever = document_loader(st.session_state.e5).as_retriever(search_kwargs={"k":5})
if "template" not in st.session_state:
    logger.info("Initiating Template ...")
    st.session_state.template = ChatPromptTemplate.from_messages(
    (
        "human",
        """System: Your name is Naser and you are my intelligent, knowledgeable, and helpful research assistant chat bot. As a proffessor, I am trying to read and understand a textbook and most often I encounter questions in my mind about the book I am reading. 
        I study the book and I come up with pieces of text that might contain just enough information to answer my question. I want you to read these text contained between <CONTEXT> and <END OF CONTEXT> and answer my question which is found between <QUESTION> and <END OF QUESTION>. You have to consider my conversation history with you based on the log between <CHAT HISTORY> and <END OF CHAT HISTORY>.
        I am NOT interested in your own prior knowledge or opinions and I want you to say I don't know if the provided information is not enough to answer my question. 
        Use three sentences maximum and keep the answer concise. 
        It is important to note that I am only interested in the topic of my question so DO NOT provide unnecessary information about other topics that might be included in the text. You have to consider that the text contains various types of names and models which are cruicial to the answer so you Must include them in your response.
            
            Human: 
            <CONTEXT>
            {context}
            <END OF CONTEXT>
            
            <CHAT HISTORY>
            <END OF CHAT HISTORY>
            
            <QUESTION>
            {question} 
            <END OF QUESTION>
            Answer:""",
        ),
    )
if "rag_chain" not in st.session_state:
    logger.info("Initiating RagChain ...")
    st.session_state.rag_chain = (
        {"context": st.session_state.retriever | format_docs, "question": translate_prompt | RunnablePassthrough()}
        | st.session_state.template
        | st.session_state.llm
        | translate_result
        | StrOutputParser()
    )
for message in st.session_state.chat_history:
    if message["src"] == "Human":
        with st.chat_message("Human"):
            st.markdown(message["text"])
    elif message["src"] == "AI":
        with st.chat_message("AI"):
            st.markdown(message["text"])
def generate_response(input_text,session):
    logger.info("Invoking prompt to chain ...")
    response = st.session_state.rag_chain.invoke(input_text)
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
        st.write_stream(generate_response(user_query,st.session_state.chat_history))

