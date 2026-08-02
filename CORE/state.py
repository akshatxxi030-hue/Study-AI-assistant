from typing import TypedDict,List,Optional,Annotated,Literal
import operator
from CORE.schemas import Plan,EvidenceItem
from langchain_core.documents import Document

class State(TypedDict):
    
    topic:str

    # Router and research memory
    needs_research:Literal["direct_answer","web_search","local_database"]
    queries:list[str]
    evidence:list[EvidenceItem]

    # Planning memory

    plan:Optional[Plan]

    # Work aggregator

    sections: Annotated[List[tuple[int, str]], operator.add]

    # Evaluator

    docs:List[Document]


    # Refiner
    refined_query: str

    good_docs: List[Document]
    partial_docs: List[Document]
    poor_docs: List[Document]
    user_choice: str
    refinement_attempts: int

    
    
    # Final output

    merged_md:str
    md_with_placeholders: str
    image_specs: List[dict]
    final: str




