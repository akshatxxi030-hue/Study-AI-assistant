import os
from typing import List
from CORE.state import State
from CORE.schemas import EvidenceItem,EvidencePack,RouterDecision,Plan
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

load_dotenv()

llm=ChatGroq(model="openai/gpt-oss-20b", temperature=0.0)




ORCHESTRATOR_SYSTEM = """You are the Master Curriculum Architect for an Advanced Biology Study AI.

Your job is to read a complex biological topic and the verified Evidence provided to you, and break it down into a highly structured, step-by-step Study Guide.

You will output a strict Plan containing EXACTLY TWO distinct Tasks. Do not create more than two.

RULES FOR PLANNING:
1. Logical Flow: Structure the tasks so the report flows logically. (e.g., Task 1: Introduction & Definition, Task 2: Core Mechanism, Task 3: Real-world Applications/Examples).
2. Evidence-Based: Only create tasks that can actually be answered using the Evidence provided. Do not create a task for a sub-topic if there is no evidence to support it.
3. Specificity: Ensure each Task has a highly specific 'goal' (e.g., "Explain how the Cas9 protein binds to DNA" instead of just "Explain CRISPR").
4. Word Counts: Assign target word counts based on the complexity of the task (e.g., 150 words for an intro, 400 words for a core mechanism).
5. Tone: Ensure the tone of the overall plan is academic, precise, yet accessible enough for a university student to understand.

Your Plan will be handed to parallel worker agents. The success of the final report depends entirely on how well you organize these instructions!
"""


async def orchestrator_node(state:State) -> dict:
    planner=llm.with_structured_output(Plan)
    evidence=state.get("evidence",[])

    plan=await planner.ainvoke(
        [
            SystemMessage(content=ORCHESTRATOR_SYSTEM),
            HumanMessage(content=
                         f"Topic:{state['topic']}\n"
                         f"Evidence:\n{[e.model_dump() for e in evidence][:16]}"
                        )
        ]
    )

    return {"plan":plan}
