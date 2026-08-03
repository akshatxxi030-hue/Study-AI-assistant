import os
from typing import List
from CORE.state import State
from CORE.schemas import EvidenceItem,EvidencePack,RouterDecision,Plan
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Send
from CORE.state import State
from langchain_groq import ChatGroq

load_dotenv()

llm=ChatGroq(model="llama-3.1-8b-instant",
             temperature=0)






def fanout_to_workers(state: State):
     plan = state.get("plan")
     evidence = state.get("evidence", [])
    
    
     if not plan or not plan.tasks:
        return []
        
     sends = []
     for task in plan.tasks:
        
        payload = {
            "task": task.model_dump(),
            "plan": plan.model_dump(),
            "evidence": [e.model_dump() for e in evidence]
        }
        sends.append(Send("worker", payload))
        
     return sends