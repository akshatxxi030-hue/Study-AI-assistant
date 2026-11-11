import os
from typing import List
from CORE.state import State
from CORE.schemas import EvidenceItem, EvidencePack, RouterDecision
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.0)

DIRECT_ANSWER_SYSTEM = """You are a concise biology expert. Answer the user's question directly based on your internal knowledge. Do not hallucinate; if you are unsure, respond that the information is not available."""

async def direct_answer_node(state: State) -> dict:
    """Generate a direct answer using the LLM without any retrieval.

    The state contains a 'topic' key with the user's question.
    Returns a dictionary with the key 'answer' that will be sent to the END node.
    """
    response = await llm.ainvoke([
        SystemMessage(content=DIRECT_ANSWER_SYSTEM),
        HumanMessage(content=state.get("topic", ""))
    ])
    return {"final_answer": response.content if hasattr(response, "content") else str(response)}
