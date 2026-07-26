from INGESTIONS.vector_store import store_embeddings,get_pinecone_index    
from INGESTIONS.embeddings import get_embeddings
from langchain_pinecone import PineconeVectorStore
import os

def get_retrievers(question):
    embedding=get_embeddings()
    vectorstore=PineconeVectorStore.from_existing_index(
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        embedding=embedding
    )

    retriever=vectorstore.as_retriever(search_kwargs={"k":5})
    docs=retriever.invoke(question)
    return docs