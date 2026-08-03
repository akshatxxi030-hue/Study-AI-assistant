from INGESTIONS.retriever import retrieve_docs
from dotenv import load_dotenv
from CORE.state import State
from CORE.schemas import EvidenceItem,RetrievalEvaluation,RefinementDecision
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.types import interrupt 
from langchain_groq import ChatGroq
load_dotenv()


EVALUATOR_SYSTEM = """
You are a retrieval evaluator for a Corrective RAG system.

Given:
1. The user's question.
2. The retrieved documents.

Determine whether the retrieved documents are sufficient to answer the question.

Return:

- retrieval_quality:
    "good"
    "partial"
    "poor"

- reason:
    Explain briefly why.

Rules:
- good -> documents fully answer the question.
- partial -> some relevant information exists but important information is missing.
- poor -> documents are mostly irrelevant or insufficient.
"""

llm=ChatGroq(model="llama-3.1-8b-instant",
             temperature=0)




async def evaluator_node(state:State) -> dict:
    evaluator_llm=llm.with_structured_output(RetrievalEvaluation)

    good_docs, partial_docs, poor_docs ,formatted_evidence=[], [], [], []

    for doc in state["docs"]:
        out=await evaluator_llm.ainvoke(
            [SystemMessage(content=EVALUATOR_SYSTEM),
             HumanMessage(content=f"Question:{state['topic']} Retrieved_chunk:{doc.page_content}"
                          ),
             ]
        )

        if out.retrieval_quality == "good":
            good_docs.append(doc)
        elif out.retrieval_quality == "partial":
            partial_docs.append(doc)
        else:
            poor_docs.append(doc)

    for doc in good_docs:
        item = EvidenceItem(
        title=doc.metadata.get("source", "Local Textbook"), 
        url=doc.metadata.get("source", "local_file"),
        content=doc.page_content,                          
        page_number=doc.metadata.get("page"),              
        needs_web_fallback=False,                          
        image_url=[]                                       
        )
        formatted_evidence.append(item)

    return {
        "good_docs": good_docs,
        "partial_docs": partial_docs,
        "poor_docs": poor_docs,
        "evidence":formatted_evidence
    }


def route_after_eval(state:State) -> str:
    if state["poor_docs"]:
        return "research"
    elif state["partial_docs"]:
        return "hitl_decision"
    else:
        return "orchestrator"
    




REFINER_SYSTEM = """You are a query refinement agent for a biology study assistant.
The student asked a question, and the documents retrieved from their study materials
were only partially relevant. Your job is to generate a better, more specific search
query that will retrieve more relevant chunks from the same document database.

Do not answer the question. Only generate a refined query and explain your reasoning
in the 'reason' field.
"""

async def hitl_decision(state: State) -> dict:
    attempts = state.get("refinement_attempts", 0)
    MAX_ATTEMPTS = 2

    if attempts >= MAX_ATTEMPTS:
        return {"user_choice": "web_search"}

    choice = interrupt({
        "message": "Not enough information in the context to answer your question. Do you want to run the search again with a refined query, or search the web?",
        "options": ["refine", "web_search"]
    })

    if choice == "refine":
        partial_content = "\n\n".join(doc.page_content for doc in state["partial_docs"])
        refiner = llm.with_structured_output(RefinementDecision)
        decision = await refiner.ainvoke([
            SystemMessage(content=REFINER_SYSTEM),
            HumanMessage(content=f"Original question: {state['topic']}\n\nPartially relevant content found:\n{partial_content}")
        ])
        return {
            "user_choice": "refine",
            "refined_query": decision.refined_query,
            "refinement_attempts": attempts + 1
        }
    else:
        return {"user_choice": "web_search"}



def route_after_hitl(state: State) -> str:
    if state["user_choice"] == "refine":
        return "retriever"
    else:
        return "research"

    
