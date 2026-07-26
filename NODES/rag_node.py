from INGESTIONS.retriever import get_retrievers
from dotenv import load_dotenv
from CORE.state import State
from CORE.schemas import EvidencePack
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

RAG_SYSTEM = """You are an Expert Data Extractor for a Biology AI.
Your job is to read raw, messy text chunks retrieved from a local PDF database. 
RULES:
1. Fix any broken sentences or words cut in half.
2. Ignore page numbers, headers, or irrelevant index text.
3. Extract the highest quality biological facts into strict EvidenceItem objects.
"""

llm=[]


def rag_node(state:State) ->dict :
    queries=state.get(queries,[])[:10]
    retriever=get_retrievers()

    raw_chunks=[]

    for q in queries:
        docs=retriever.invoke(q)

        for d in docs:
            raw_chunks.append(d.page_content)

        if not raw_chunks:
            return {"evidence":[]}
        
        extractor=llm.with_structured_output(EvidencePack)

        pack : EvidencePack=extractor.invoke([
            SystemMessage(content=RAG_SYSTEM),
            HumanMessage(content=
                         f"Topic:{state['topic']}\n"
                         f"PDF chunks:\n{raw_chunks}")

        ])

    return{"evidence":pack.evidence}