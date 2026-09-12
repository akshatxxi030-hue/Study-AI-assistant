import os
from typing import List
from CORE.state import State
from CORE.schemas import EvidenceItem,EvidencePack,RouterDecision,Plan,Task
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import time
import random

load_dotenv()

llm=ChatGroq(model="openai/gpt-oss-120b", temperature=0.0)


WORKER_SYSTEM = """You are an Expert Academic Writer for a Biology Study AI.

Your job is to write ONE specific section of a comprehensive biology study guide. 
You will be provided with:
1. The overall Plan (so you know the context).
2. Your specific Task instructions (what you must write).
3. Verified Evidence (the facts you must use).

RULES FOR WRITING:
1. Strict Grounding: You MUST base all biological facts, dates, and statistics ONLY on the provided Evidence. Do not invent or hallucinate new facts from your internal memory. 
2. Language Refinement: Use your advanced linguistic skills to weave the raw Evidence bullet points into a beautiful, easy-to-read academic narrative. Explain complex terms simply.
3. Formatting: Output your answer in pure Markdown format. Use `###` for sub-headers, `-` for bullet points, and `**bold**` for key terms. Do NOT output JSON.
4. Constraints: You must strictly adhere to the 'target_words' count specified in your Task instructions. Do not write a 500-word essay if the target is 150 words.
5. Citations: If the Task requires it, cite your sources by mentioning the Evidence Title or URL naturally in the text.
6. Images: You will be provided with a list of Image URLs in your evidence. You MUST embed at least one relevant image into your Markdown response using standard syntax: `![Description of Image](Image URL)`

Only return the Markdown text for your specific section. Do not write an introduction or conclusion unless your Task explicitly tells you to.
"""


async def worker_node(payload:dict) -> dict:
    
    task = Task(**payload["task"])
    plan = Plan(**payload["plan"])
    evidence = [EvidenceItem(**e) for e in payload.get("evidence", [])]
    
    bullets_text = "\n- " + "\n- ".join(task.bullets)
    
    section_response = await llm.ainvoke([
        SystemMessage(content=WORKER_SYSTEM),
        HumanMessage(
            content=(
                f"Research Title: {plan.research_title}\n\n"
                f"Tone:{plan.tone}\n"
                f"Constraints: {plan.constraints}\n"
                f"Your Specific Task: {task.title}\n"
                f"Your Goal: {task.goal}\n"
                f"Target Words: {task.target_words}\n"
                f"Required Bullet Points to cover: {bullets_text}\n\n"
                f"needs_research: {task.needs_research}\n"
                f"Evidence to use:\n{[e.model_dump() for e in evidence][:15]}"
            )
        )
    ])
    
    content = section_response.content
    if isinstance(content, list):
        content = content[0].get("text", "") if isinstance(content[0], dict) else str(content)
    generated_md = content.strip()
    
    return {"sections": [(task.id, generated_md)]}
    

    
