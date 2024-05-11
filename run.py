# from loaders.dataloader import translator
import pandas as pd

if __name__ == "__main__":
    
    filepath = "assets/framed_translate.csv"
    
    base_data = pd.read_csv(filepath,encoding="utf-8-sig")
    # base_data.set_index("idx",inplace=True)
    base_data.columns = [["id","parent","topic","page_content_en","page_content_fa"]]
    for _,i in base_data.iterrows():
        print(i["page_content"])