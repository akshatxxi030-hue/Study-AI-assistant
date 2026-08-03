import os
from typing import List
from CORE.state import State
from CORE.schemas import EvidenceItem,EvidencePack,RouterDecision
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
     model="llama-3.1-8b-instant",
     temperature=0.0 
)



ROUTER_SYSTEM = """You are the master routing agent for an Advanced Biology Study AI. 
Your only job is to analyze the student's question and decide the most efficient way to answer it.

You have three choices for routing:

1. "direct_answer": 
- Choose this if the question is about fundamental, unchanging biology concepts (e.g., "What is Mitosis?", "Explain the structure of DNA", "What is the mitochondria?").
- These are questions you can answer confidently from your internal training data without hallucinating.
- Direct_answer is for definitions and concepts that are the same regardless of source — any textbook, any course, would explain them identically. local_database is for anything where the specific source matters — the student's own materials, their professor's framing, examples or diagrams unique to their course — even if they don't explicitly say 'my textbook' or 'page X'."

2. "web_search": 
- Choose this if the question is about recent discoveries, highly specific clinical trials, cutting-edge CRISPR technology, or extremely niche bioinformatics.
- Choose this if the user explicitly asks for "latest news" or "recent papers".

IF you choose "web_search":
- You MUST generate 3 to 10 highly technical, distinct search queries.
- Write the queries like an academic researcher (e.g., instead of "new cancer drug", use "2026 targeted oncology immunotherapy clinical trials").

IF you choose "direct_answer":
- Leave the queries list completely empty [].


3."local_database":
   - Choose this if the question is about topics covered in the student's 
     uploaded textbooks and study materials.
   - This searches the student's personal PDF database first before 
     going to the internet.

CRITICAL RULE: Do NOT answer the user's biology question in the 'reason' field. The 'reason' field is only for explaining your routing logic (e.g., "This is a fundamental concept, no search needed.").
"""

async def router_node(state:State) -> dict:
    decider=llm.with_structured_output(RouterDecision)
    decision=await decider.ainvoke(
        [
        SystemMessage(content=ROUTER_SYSTEM),
        HumanMessage(content=f"Topic:{state['topic']}")
        ]
    )
    return{
        "needs_research":decision.needs_research,
        "queries":decision.queries
    }


def route_next(state:State)-> str:
    if state["needs_research"] == "web_search":
        return "research"
    elif state["needs_research"] == "local_database":
        return "local_database"
    elif state["needs_research"] == "direct_answer":
        return "direct_answer"
    else:
        return "orchestrator"


