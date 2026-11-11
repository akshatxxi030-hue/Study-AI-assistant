from CORE.state import State

def merge_node(state:State) -> dict:

    sections=state.get("sections",[])
    plan=state.get("plan")

    if not sections:
        return{"merged_md": "No content found"}
        
    sort_sections=sorted(sections,key=lambda x:x[0])
    body_text = "\n\n".join([text for task_id, text in sort_sections]).strip()
    title = plan.research_title if plan else state.get("topic", "Biology Report")
    final_markdown = f"# {title}\n\n{body_text}\n"

    return {"final_answer":final_markdown}