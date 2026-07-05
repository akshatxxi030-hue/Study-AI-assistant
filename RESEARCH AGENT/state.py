from typing import TypedDict,List,Optional,Annotated
import operator
from schemas import Plan,EvidenceItem

class State(TypedDict):
    
    topic:str

    # Router and research memory
    needs_research:bool
    queries:list[str]
    evidence:list[EvidenceItem]

    # Planning memory

    plan:Optional[Plan]

    # Work aggregator

    sections: Annotated[List[tuple[int, str]], operator.add]
    
    # Final output

    merged_md:str
    md_with_placeholders: str
    image_specs: List[dict]
    final: str




