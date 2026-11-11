from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_text(documents):
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200
        )
        
    chunks=splitter.split_documents(documents)
    return chunks
