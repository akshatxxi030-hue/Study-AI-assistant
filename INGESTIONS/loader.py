from langchain_community.document_loaders import PyPDFLoader

def pdf_loader(file_path:str):
    loader=PyPDFLoader(file_path)
    documents= loader.load()
    return documents