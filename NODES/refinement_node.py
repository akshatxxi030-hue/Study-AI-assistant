from INGESTIONS.retriever import get_retrievers
from dotenv import load_dotenv
from CORE.state import State
from CORE.schemas import EvidencePack,RetrievalEvaluation
from langchain_core.messages import SystemMessage, HumanMessage


llm=[]