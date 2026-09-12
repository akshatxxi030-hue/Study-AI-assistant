from langchain_huggingface import HuggingFaceEndpointEmbeddings
import os

def get_embeddings():
    return HuggingFaceEndpointEmbeddings(
        model="Qwen/Qwen3-Embedding-0.6B",
        huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY")
    )
   
   