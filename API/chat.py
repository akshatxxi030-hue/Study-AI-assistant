# api/chat.py
from fastapi import APIRouter,Request
from langgraph.types import Command
import uuid
from CORE.schemas import ChatRequest,ResumeRequest

router = APIRouter()



@router.post("/chat")
async def chat(req: ChatRequest,request:Request):
    graph = request.app.state.graph
    session_id = req.session_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    result = await graph.ainvoke({"topic": req.message}, config=config)

    if "__interrupt__" in result:
        return {
            "session_id": session_id,
            "needs_input": True,
            "question": result["__interrupt__"][0].value
        }

    answer_text = result.get("final_answer") or result.get("answer") or result.get("merged_md") or result.get("final") or ""
    return {
        "session_id": session_id,
        "needs_input": False,
        "answer": answer_text
    }


    

@router.post("/resume")
async def resume(req: ResumeRequest,request:Request):
    graph = request.app.state.graph
    config = {"configurable": {"thread_id": req.session_id}}

    result = await graph.ainvoke(Command(resume=req.choice), config=config)

    if "__interrupt__" in result:
        return {
            "session_id": req.session_id,
            "needs_input": True,
            "question": result["__interrupt__"][0].value
        }

    answer_text = result.get("final_answer") or result.get("answer") or result.get("merged_md") or result.get("final") or ""
    return {
        "session_id": req.session_id,
        "needs_input": False,
        "answer": answer_text
    }