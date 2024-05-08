
# from bb_assistant.llm import aya
# import json

# def format_docs(docs):
#     clean_docs = []
#     for doc in docs:
#         try:
#             clean_docs.append(doc.metadata["eng_content"].replace(":"," "))
#         except Exception as fail:
#              print(f"failed to collect english content {fail}")
        
#     with open("retrieved.json","w") as f:
#         json.dump(clean_docs,f,ensure_ascii=False,indent=4)
#     return "\n\n".join(clean_docs)


# def translate_prompt(prompt:str):
#     result = aya.Aya101LLM()._call(
#         f"Translate the following text from perisan to english then summerize it to usefull sentences: \n {prompt}"
#     )
#     print("TRANSLATED PROMPT :",result)
#     return result
# def translate_result(prompt: str):
#     prompt.replace(":"," ")
#     return aya.Aya101LLM()._call(
#         f"Translate the following text from English to Persian: {prompt}"
#     )