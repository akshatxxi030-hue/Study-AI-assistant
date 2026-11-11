from INGESTIONS.retriever import retrieve_docs
from CORE.state import State

async def retriever_node(state: State) -> dict:
    query = state.get("refined_query") or state["topic"]
    docs = await retrieve_docs(query)
    return {"docs": docs}