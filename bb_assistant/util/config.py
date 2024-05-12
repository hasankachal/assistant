from dataclasses import dataclass
import os
PROXY_URI = os.getenv("PROXY","http://127.0.0.1:2080")

class BaseConfig:
    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                attr = getattr(self, k)
                if isinstance(v, dict):
                    assert attr is None or isinstance(attr, (BaseConfig, dict)), \
                        f"Expected {k} to be a dict, BaseConfig or None, got {type(attr)}"
                    attr.update(**v)
                else:
                    setattr(self, k, v)
            else:
                raise AttributeError(f"Invalid attribute {k}")


# api metrics taken from commandline on startup
@dataclass
class Api_Metrics(BaseConfig):
    host: str = '0.0.0.0'
    port: int = 5526
    num_workers: int = 4
    version: str = 'v2'
    loglevel:str = "info"

# ACCOUNT_TOKENS = {
#     'm-uid':'1500740041',
#     'm-login':'1; Path=/; Domain=quora.com; Expires=Sat, 18 Apr 2026 00:05:14 GMT',
#     'm-b_lax':'PH2DFI93zJ8b_IPzqNHFEA==; Path=/; Domain=quora.com; Secure; HttpOnly; Expires=Fri, 17 Apr 2026 12:05:14 GMT',
#     'm-b_strict':'PH2DFI93zJ8b_IPzqNHFEA==; Path=/; Domain=quora.com; Secure; HttpOnly; Expires=Fri, 17 Apr 2026 12:05:14 GMT',
#     'm-b': 'PH2DFI93zJ8b_IPzqNHFEA==; Path=/; Domain=quora.com; Secure; HttpOnly; Expires=Fri, 17 Apr 2026 12:05:14 GMT',
#     'm-s':'lrqgM0Pzz0IIufRgisSNmg==; Path=/; Domain=quora.com; Secure; HttpOnly; Expires=Fri, 17 Apr 2026 12:05:14 GMT',
#     'm-lat': '/S+avRa6ZqNjCXfxzgO8RPBn55a41g+flJvQEUk0Ug==',
#     'p-b':'fflBQAr2k2qx_9BULWhxwA%3D%3D; Path=/; Expires=Fri, 17 Apr 2026 09:53:58 GMT; Max-Age=63072000; Secure; HttpOnly; SameSite=none'

# }

ACCOUNT_TOKENS2 = {
    "m-s":"VRb1YlmkF9sC5qt_GjtD-Q==; Domain=.quora.com; Max-Age=63072000; Path=/; expires=Thu, 23-Apr-2026 15:34:36 GMT; secure; HttpOnly",
    "m-uid":"2546200021; Path=/; Domain=quora.com; Expires=Fri, 24 Apr 2026 03:24:42 GMT",
    "m-login":"1; Domain=.quora.com; Max-Age=63115200; Path=/; expires=Fri, 24-Apr-2026 03:34:36 GMT",
    "m-b":"ZtXgW8vu1OPMMWcrI_q8zA==; Domain=.quora.com; Max-Age=63072000; Path=/; expires=Thu, 23-Apr-2026 15:34:36 GMT; secure; HttpOnly; SameSite=None",
    "m-b_lax":"ZtXgW8vu1OPMMWcrI_q8zA==; Domain=.quora.com; Max-Age=63072000; Path=/; expires=Thu, 23-Apr-2026 15:34:36 GMT; secure; HttpOnly; SameSite=Lax",
    "m-b_strict":"ZtXgW8vu1OPMMWcrI_q8zA==; Domain=.quora.com; Max-Age=63072000; Path=/; expires=Thu, 23-Apr-2026 15:34:36 GMT; secure; HttpOnly; SameSite=Strict",
    "m-lat":"IBnPFBbUdxdJ5LFYPPqUuWyw9hKqKCgNobPX0HfWGw=="
    
}
def shred_cookies(dictionary):
    formatted_pairs = []
    for key, value in dictionary.items():
        formatted_pairs.append(f"{key}={value}")
    result_string = "; ".join(formatted_pairs)
    return result_string 

    
GLOBAL_HEADERS = {
"accept":"multipart/mixed; deferSpec=20220824, application/json",
"quora-formkey":"d46531f9bc9f3c21d187a4a232dadd5d",
"quora-tchannel":"poe-chan57-8888-rmksxcluozhovypdbsay",
"user-agent":"Poe a2.39.8 rv:3918 env:prod (SM-S908E; Android OS 9; en_US)",
"poe-language-code":"en",
"content-type":"application/json",
"cookie":shred_cookies(ACCOUNT_TOKENS2)
}

HTTP_PROXY = {
    "https":PROXY_URI, 
    "http":PROXY_URI}


