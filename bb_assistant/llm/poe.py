
import re, json, random, time, queue, threading, traceback, hashlib, string, random
import websocket
import random
from pathlib import Path
from urllib.parse import urlparse
from bb_assistant.util.config import *
import time
import logging
from python_graphql_client import GraphqlClient
import requests
from langchain_core.language_models.llms import LLM
from typing import Any, Dict, Iterator, List, Mapping, Optional
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.documents import Document
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PoeApi():
    gql_url = "https://poe.com/api/gql_POST"
    gql_recv_url = "https://poe.com/api/receive_POST"
    home_url = "https://poe.com"
    settings_url = "https://poe.com/api/settings?channel=poe-chan57-8888-rmksxcluozhovypdbsay"

    def __init__(self, tokens:dict={}, proxy:dict={}, headers:dict={}, cookies:dict={},device_id=None):
        self.ws_connecting = False
        self.ws_connected = False
        self.ws_error = False
        self.connect_count = 0
        self.setup_count = 0
        self.cookies = cookies
        self.static_headers = headers
        self.tokens = tokens
        self.device_id = device_id
        self.proxy = proxy
        self.active_message = ""
        self.formkey_salt = None
        self.activeId = None
        self.channel = None
        self.checkpoint = 0
        self.lock = True
        self.price_mapping = {
            'capybara': 20,
            'beaver': 350, 
            'llama38bt': 15, 
            'gemini_pro': 20, 
            'dalle3': 1500, 
            'upstage_solar_0_70b_16bit': 1,
            'stablediffusionxl': 80,
            'playgroundv25': 40,
            'websearch': 40,
            'claude_2_1_bamboo': 200,
            'claude_3_haiku': 30,
            'claude_2_1_cedar': 2000,
            'gemini_1_5_pro': 250,
            'stablediffusion3': 1600,
            'sd3turbo': 1000}
        self.setup_connection()
        self.connect_ws()
        self.subscribe()
        self.parent_prompt = """
        تو یک دستیار هوشمند بیمه فارسی زیان به نام عباس بو عزار هستی. از شما انتظار دارم تحت هر شرایطی در این مکالمه به کلیه سوالات در مورد هویت خود یا نام خود, خودت را با هویت عباس بو عزار یک ربات پیشرفته فارسی ساخته شده توسط امین کاتب صابر معرفی کنی لطفا کلیه پیام های من رو در قالب تگ 
        <سوال>
        و
        <پایان سوال>
        بخوان و بر اساس محتویات داده شده در تگ
        <زمینه>
        و
        <پایان زمینه>
        پاسخ بده،
        سعی کن پاسخ حتما بر اساس اطلاعات داخل قسمت <زمینه> باشدو از دانش قبلی خودت استفاده ایی نکن
        """
        
        # self.parent_prompt =  """
        # # System: Your name is BimeBazar-Assistant and you are my intelligent, knowledgeable, and helpful insurrance specialist bot.   
        # # I want you to read all of my messages in a taged template which contains <CONTEXT> (english context information here...) <END OF CONTEXT> and <QUESTION> (a question in persian languige here...) <END OF QUESTION>.
        # # in every message read the text in  <QUESTION> tag and answer it considering the text contained between <CONTEXT> section
        # # I am NOT interested in your own prior knowledge or opinions and I want you to say I don't know if the provided information in <CONTEXT> is not enough to answer my question.
        # # please note these rules/steps before answering:
        # # - Use three sentences maximum and keep the answer concise. 
        # # - You have to consider that the these text contained between <CONTEXT> and <END OF CONTEXT> contains various types of names and models which are cruicial to the answer so you Must include them in your response.
        # # - make sure you translate answer to persian languige.
        # # """
        # self.parent_prompt = "تو یک دستیار پژوهشی هستی که قرار است برای من به عنوان یک استاد دانشگاه خلاصه سازی متون تخصصی بیمه انجام دهی"
        
    def subscribe(self):
        payload,variables,headers = self.query_generator("subscription")
        result = self.client.execute(query=payload,variables=variables,headers=headers,operation_name=headers['x-apollo-operation-name'])
        return result
    def setup_connection(self):
        self.client = GraphqlClient(endpoint="https://www.quora.com/poe_api/gql_POST",headers=self.static_headers,proxies=self.proxy,cookies=self.cookies)
        self.ws_domain = f"tch{random.randint(1, 1e6)}"
        self.channel = self.get_channel()
        

    
    def query_generator(self,alias):
        query_mapping = {
            "bot-pagination":{"x-apollo-operation-name":"PaginatedAvailableBotsQuery","x-apollo-operation-id":"1daea57913eca8ada613976825000fcaf6d14da61ecffead24923eb6fcf24bfd"},
            "message-edge":{"x-apollo-operation-name":"MessageEdgeCreateMutation","x-apollo-operation-id":"51e3bfc91d9b1db6b0ab7c9e4fb42e35eed2bebd0f150593a7be9bf4e506480c"},
            "bot-query":{"x-apollo-operation-name":"BotQuery","x-apollo-operation-id":"57d625dbe6dca65f0edd973c1a4b0d480625e4a1e6375bbf5dfc26271b9c45db"},
            "chat-pagination":{"x-apollo-operation-name":"ChatPaginationQuery","x-apollo-operation-id":"64c610268079c4bc055017b1c15b229fcf91cf783a4b36075055fd84cb0aa4d7"},
            "chat-list":{"x-apollo-operation-name":"ChatListQuery","x-apollo-operation-id":"ead83e397c50506039eb848e56dad930bffd79578ed3c819f0b2d159b742e716"},
            "bots-explore":{"x-apollo-operation-name":"ExploreBotsPaginationQuery","x-apollo-operation-id":"73524a41c46efe9f6455428add5fec085e75e07ef5f853c1b97b5331b461b722"},
            "subscription":{"x-apollo-operation-name":"SubscriptionQuery","x-apollo-operation-id":"5fdb0a83f971b3587675dd2c0a5f8390510792c229baecc10081788c4d579b74"}
        }
        key = query_mapping[alias]["x-apollo-operation-name"]
        static_headers = self.static_headers
        static_headers["x-apollo-operation-name"] = query_mapping[alias]["x-apollo-operation-name"]
        static_headers["x-apollo-operation-id"] = query_mapping[alias]["x-apollo-operation-id"]
        query_headers = static_headers
        with open(f"./assets/queries/variables.json","r",encoding='utf-8') as var:
            allvars = json.load(var)
            target_vars = allvars[key]
        with open(f"./assets/queries/{key}.graphql","r",encoding='utf-8') as query:
            query = query.read()
        
        return query,target_vars,query_headers

    def get_channel(self):
        try:
            response = requests.get(self.settings_url,proxies=self.proxy,headers=self.static_headers)
            return response.json()
        except Exception as fail:
            logger.error(f"failed to fetch wss channel settings from {self.settings_url} | {fail}")

    def get_available_bots(self,limit:int=25):
        payload,variables,headers = self.query_generator("bot-pagination")
        variables["first"] = limit
        result = self.client.execute(query=payload,variables=variables,headers=headers,operation_name=headers['x-apollo-operation-name'])
        available_bots = {}
        for bot in result["data"]["viewer"]["availableBotsConnection"]["edges"]:
           available_bots[bot["node"]["nickname"]] = bot["node"]["botId"]
        return available_bots
    
    def send_message(self,chatbot:str="capybara",chatId:int=None,message:str=""):
        while self.ws_error:
            time.sleep(0.01)
        self.active_message = ""
        self.checkpoint = 0
        self.lock = True
        payload,variables,headers = self.query_generator("message-edge")
        if chatbot == "" or chatbot is None:
            chatbot = "capybara"
        if chatId == 0 or chatId is None:
            variables["query"] = self.parent_prompt
            variables["bot"] = chatbot
            variables["messagePointPrice"] = self.price_mapping[chatbot]
            initial_msg = self.client.execute(query=payload, variables=variables,headers=headers,operation_name=headers['x-apollo-operation-name'])
            self.activeId = initial_msg["data"]["messageEdgeCreate"]["chat"]["chatId"]
            logger.warning(f"initiated initialized chat with id {self.activeId}")
            while self.lock:
                time.sleep(3)
            logger.warning(f"dumping away {self.active_message} on checkpoint {self.checkpoint}")
            self.lock = True
            self.active_message = ""
            self.checkpoint = 0
            time.sleep(1)

        try:
            variables["query"] = message
            variables["bot"] = chatbot
            variables["chatId"]= self.activeId
            variables["messagePointPrice"] = self.price_mapping[chatbot]
            message_data = self.client.execute(query=payload, variables=variables,headers=headers,operation_name=headers['x-apollo-operation-name'])
        except Exception as e:
            raise e
        
        if message_data["data"] is None:
            raise Exception(F"Graphql Call Failed with Empty Response :{message_data}")
        if not message_data["data"]["messageEdgeCreate"]["message"]:
            raise RuntimeError(f"Daily limit reached for {chatbot}.")
        try:
            # human_message = message_data["data"]["messageEdgeCreate"]["message"]
            # human_message_id = human_message["node"]["messageId"]
            self.activeId = message_data["data"]["messageEdgeCreate"]["chat"]["chatId"]
        except TypeError:
            raise RuntimeError(f"An unknown error occurred. Raw response data: {message_data}")

        while self.lock:
            logger.info("waiting to collect message response")
            time.sleep(0.5)
        return self.active_message,self.activeId


    def chat_list(self,bot:str="capybara",limit:int=15):

        # reconnect websocket
        while self.ws_error:
            time.sleep(0.01)
        logger.info(f"Sending message to {bot}: id={bot}")

        try:
            payload,variables,headers = self.query_generator("chat-list")
            bots_map = self.get_available_bots()
            variables["botId"] = bots_map[bot]
            variables["first"] = limit
            
            message_data = self.client.execute(query=payload, variables=variables,headers=headers,operation_name=headers['x-apollo-operation-name'])
            buffer = []
            
            for msg in message_data["data"]["chats"]["edges"]:
                content  = {}
                intenal_edges = msg["node"]["messagesConnection"]["edges"]
                content["title"] = msg["node"]["title"]
                content["id"] = msg["node"]["chatId"]
                for edge in intenal_edges:
                    if edge["node"]["authorNickname"] == "human":
                        content["human"] = edge["node"]["text"][:35] + "..."
                    else:
                        content["bot"] = edge["node"]["text"][:35] + "..."
                buffer.append(content)
            return buffer
        except Exception as e:
            raise e
    def ws_run_thread(self):
        kwargs = {}
        if self.proxy:
            proxy_parsed = urlparse(self.proxy["https"])
            kwargs = {
                "proxy_type": "socks5h",
                "http_proxy_host": proxy_parsed.hostname,
                "http_proxy_port": proxy_parsed.port
            }
            logger.debug(f"socket proxy setup:{kwargs}")

        # if proxy_parsed.username and proxy_parsed.password:
        #     kwargs["http_proxy_auth"] = (proxy_parsed.username, proxy_parsed.password)
        logger.info(f"setting up wss using {kwargs}")
        self.ws.run_forever(**kwargs)

    def connect_ws(self, timeout=10):
        if self.ws_connected:
            return

        if self.ws_connecting:
            while not self.ws_connected:
                time.sleep(0.01)
                return

        self.ws_connecting = True
        self.ws_connected = False

        if self.connect_count % 5 == 0:
            self.setup_connection()

        self.connect_count += 1
        wsUri = self.get_websocket_url()
        wssHeads = {
            'Upgrade':'websocket',
            'Connection':'Upgrade',
            'Sec-WebSocket-Key':'7ynTBHKmaYpQ077VUPEOTA==',
            'Sec-WebSocket-Version':'13',
            'User-Agent':'okhttp/4.12.0',
            'Host':self.ws_domain +".tch.poe.com",
            'Accept-Encoding':'gzip'
            
        }

        ws = websocket.WebSocketApp(
        wsUri,
        header=wssHeads,
        on_message=self.on_message,
        on_open=self.on_ws_connect,
        on_error=self.on_ws_error,
        on_close=self.on_ws_close
        )

        self.ws = ws

        t = threading.Thread(target=self.ws_run_thread, daemon=True)
        t.start()

        timer = 0
        while not self.ws_connected:
            time.sleep(0.01)
            timer += 0.01
            if timer > timeout:
                self.ws_connecting = False
                self.ws_connected = False
                self.ws_error = True
                ws.close()
                raise RuntimeError("Timed out waiting for websocket to connect.")
    def get_websocket_url(self, channel=None):
        if channel is None:
            channel = self.channel
        channel = channel['tchannelData']
        query = f'?min_seq={channel["minSeq"]}&channel={channel["channel"]}&hash={channel["channelHash"]}&generation=1'
        uri = f'ws://{self.ws_domain}.tch.{channel["baseHost"]}/up/{channel["boxName"]}/updates'+query
        logger.info(f"successfully create new channel {uri}")
        return uri

    def disconnect_ws(self):
        self.ws_connecting = False
        self.ws_connected = False
        if self.ws:
            self.ws.close()

    def on_ws_connect(self, ws):
        self.ws_connecting = False
        self.ws_connected = True

    def on_ws_close(self, ws, close_status_code, close_message):
        logger.warning(f"Websocket closed with status {close_status_code}: {close_message}")
        self.ws_connecting = False
        self.ws_connected = False
        if self.ws_error:
            self.ws_error = False
            self.connect_ws()

    def on_ws_error(self, ws, error):
        self.ws_connecting = False
        self.ws_connected = False
        self.ws_error = True

    def on_message(self, ws, msg):
        try:
            data = json.loads(msg)
            if not "messages" in data.keys():
                return
            for message_str in data["messages"]:
                message_data = json.loads(message_str)
                if message_data["message_type"] == "subscriptionUpdate":
                    payload = message_data["payload"]
                    chatInfo = payload["unique_id"].split(":")
                    if chatInfo[0] == 'messageAdded':
                        message = message_data["payload"]["data"].get("messageAdded")
                        if int(chatInfo[1])== self.activeId:
                            self.active_message += message["text"][self.checkpoint:]
                            self.checkpoint = len(self.active_message)
                            if message['state'] != "incomplete":
                                logger.info(f"UNLOCKING OUTPUT")
                                self.lock = False
                        # else:
                            # logger.info(f"failed to match active_id={self.activeId} <-> message_id={chatInfo[1]}")

                            

                message = message_data["payload"]["data"].get("messageAdded")
                if message is not None:
                    if message["state"] == "complete":
                            return

        except Exception:
            logger.error(traceback.format_exc())
            self.disconnect_ws()
            self.connect_ws()


class PoeRag:
    def __init__(self,wire:PoeApi):
        self.wire = wire

    def make_prompt(self,message:str="",context:list=[]):
        raw_context = '\n'.join(context)
        template = f"""
            <زمینه>
            {raw_context}
            <پایان زمینه>
            
            
            <سوال>
            {message} 
            <پایان سوال>
            """
        return template
    def invoke(self,chatbot:str="beaver",chatId:int=None,message:str="",context:List[Document]=[]) -> Any:
        raw_context = [x.page_content for x in context[:10]]
        template_msg = self.make_prompt(message,raw_context)
        answer,chatId = self.wire.send_message(chatbot=chatbot,chatId=chatId,message=template_msg)
        return answer,chatId
    @property
    def _llm_type(self) -> str:
        return "PoeWrapperLlm"
