from bb_assistant.util.logging import logger
from bb_assistant.util.config import *
from bb_assistant.llm.poe import PoeApi
import streamlit as st
import time
WRAPPER = None

st.set_page_config(layout='wide')


st.title('🦜🔗 INTELIX')
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
    st.session_state.chat_history = []
if "chat_id" not in st.session_state:
    st.session_state.chat_id = 0
if "wrapper" not in st.session_state:
    st.session_state.wrapper = PoeApi(ACCOUNT_TOKENS2,headers=GLOBAL_HEADERS,proxy=HTTP_PROXY,cookies=ACCOUNT_TOKENS2)


def click_button():
    st.session_state.chat_history = []
    st.session_state.chat_id = 0
    st.session_state.wrapper = PoeApi(ACCOUNT_TOKENS2,headers=GLOBAL_HEADERS,proxy=HTTP_PROXY,cookies=ACCOUNT_TOKENS2)

st.button("Reset", type="primary",on_click=click_button)
for message in st.session_state.chat_history:
    if message["src"] == "Human":
        with st.chat_message("Human"):
            st.markdown(message["text"])
    elif message["src"] == "AI":
        with st.chat_message("AI"):
            st.markdown(message["text"])
def generate_response(input_text,session):

    response,chatid = st.session_state.wrapper.send_message(chatbot="beaver",chatId=st.session_state.chat_id,message=input_text)
    st.session_state.chat_id = chatid
    session.append({"src":"AI","text":response})
    st.caption(f"chat Id {st.session_state.chat_id}")
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

