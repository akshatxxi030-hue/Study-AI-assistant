from INGESTIONS.embeddings import get_embeddings
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import os

load_dotenv()

def get_pinecone_index():
    pc=Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    return pc.Index(os.getenv("PINECONE_INDEX_NAME"))

def store_embeddings(chunks):
    embedding=get_embeddings()
    vectorstore=PineconeVectorStore.from_documents(
        chunks,
        embedding,
        index_name=os.getenv("PINECONE_INDEX_NAME")

    )
    return vectorstore