from __future__ import annotations
from typing import TypedDict, List, Optional, Literal, Annotated
from pydantic import BaseModel, Field

class Task(BaseModel):
    id:int
    title:str
    goal:str = Field(...,description="One sentence describing what the what the reader should understand")
    bullets:List[str] = Field(min_length=3,max_length=8)
    target_words:int =Field(...,description="Traget words(200-600)")
    needs_research:bool=False
    needs_references:bool=False


class Plan(BaseModel):
    research_title:str
    student:str
    tone:str
    constraints:List[str]=Field(default_factory=list)
    tasks:list[Task]


class EvidenceItem(BaseModel):
    title:str
    url:str
    published_at:Optional[str]
    source:Optional[str]
    content:str = Field(..., description="The actual extracted biological facts, text, or chunk.")
    page_number: Optional[int] = None 
    needs_web_fallback: bool
    image_url:List[str]= Field(default_factory=list)


class RouterDecision(BaseModel):
    needs_research:Literal["direct_answer","web_search","local_database"]
    reason:str
    queries:list[str]=Field(default_factory=list)
    max_results_per_query:int=Field(5)


class EvidencePack(BaseModel):
    evidence:list[EvidenceItem]=Field(default_factory=list)


class RetrievalEvaluation(BaseModel):
    retrieval_quality: Literal["good", "partial", "poor"]
    reason: str

class RefinementDecision(BaseModel):
    refined_query: str
    reason: str

class ChatRequest(BaseModel):
    message:str
    session_id:Optional[str]=None

class ResumeRequest(BaseModel):
    session_id: str
    choice: str  



class ImageSpec(BaseModel):
    placeholder: str = Field(..., description="e.g. [[IMAGE_1]]")
    filename: str = Field(..., description="Save under images/, e.g. qkv_flow.png")
    alt: str
    caption: str
    prompt: str = Field(..., description="Prompt to send to the image model.")
    size: Literal["1024x1024", "1024x1536", "1536x1024"] = "1024x1024"
    quality: Literal["low", "medium", "high"] = "medium"



class GlobalImagePlan(BaseModel):
    md_with_placeholders: str
    images: List[ImageSpec] = Field(default_factory=list)




    
    


