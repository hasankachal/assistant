from loaders.dataloader import translator,test_rag
# import torch
import json
import pandas as pd
def read_eng():
    with open("assets/trans.json","r",encoding='utf-8') as file:
        content = json.load(file)
    return content
if __name__ == "__main__":
    # translator()
    test_rag()
