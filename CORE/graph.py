from langgraph.graph import StateGraph,START,END
from CORE.state import State
from NODES.router_node import router_node,route_next
from NODES.worker_node import worker_node
from NODES.orchestrator_node import orchestrator_node
from NODES.research_node import research_node
from NODES.fanout import fanout_to_workers
from NODES.reducer import merge_node
from NODES.retriever_node import retriever_node
from NODES.crag_node import evaluator_node, route_after_eval, hitl_decision, route_after_hitl
from NODES.direct_answer_node import direct_answer_node
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import os

g=StateGraph(State)


g.add_node("router", router_node)
g.add_node("research", research_node)
g.add_node("retriever", retriever_node)
g.add_node("evaluator", evaluator_node)
g.add_node("hitl_decision", hitl_decision)
g.add_node("orchestrator", orchestrator_node)
g.add_node("worker", worker_node)
g.add_node("reducer", merge_node)
g.add_node("direct_answer", direct_answer_node)


g.add_edge(START, "router")


g.add_conditional_edges("router", route_next, {
    "research": "research", 
    "orchestrator": "orchestrator",
    "local_database": "retriever",
    "direct_answer": "direct_answer"
})

# RAG & CRAG Loop
g.add_edge("retriever", "evaluator")
g.add_conditional_edges("evaluator", route_after_eval, {
    "research": "research",
    "hitl_decision": "hitl_decision",
    "orchestrator": "orchestrator"
})

# Human-In-The-Loop routing
g.add_conditional_edges("hitl_decision", route_after_hitl, {
    "retriever": "retriever",
    "research": "research"
})

# Direct answer path
g.add_edge("direct_answer", END)

g.add_edge("research", "orchestrator")

g.add_conditional_edges("orchestrator", fanout_to_workers, ["worker"])
g.add_edge("worker", "reducer")
g.add_edge("reducer", END)

from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = g.compile(checkpointer=memory)

