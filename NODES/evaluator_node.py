from INGESTIONS.retriever import get_retrievers
from dotenv import load_dotenv
from CORE.state import State
from CORE.schemas import EvidencePack,RetrievalEvaluation
from langchain_core.messages import SystemMessage, HumanMessage

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

llm=[]


def evaluator_node(state:State) -> dict:
    evaluator_llm=llm.with_structured_output(RetrievalEvaluation)

    filtered_docs=[]

    for doc in state["docs"]:
        out=evaluator_llm.invoke(
            [SystemMessage(content=EVALUATOR_SYSTEM),
             HumanMessage(content=f"Question:{state['question']} Retrieved_chunk:{doc.page_content}"
                          ),
             ]
        )

        if out.retrieval_quality in ("good"):
            filtered_docs.append(doc)

    return {
        "filtered_docs": filtered_docs,
        }


def hitl(state:State) -> dict:
    x=[]

