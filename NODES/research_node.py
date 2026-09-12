import os
from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults
from CORE.state import State
from CORE.schemas import EvidenceItem,EvidencePack,RouterDecision
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

load_dotenv()

llm=ChatGroq(model="openai/gpt-oss-120b", temperature=0.0)



from tavily import TavilyClient

def tavily_search(query:str , max_results:int=3) -> dict:
    if not os.getenv("TAVILY_API_KEY"):
        print("WARNING : TAVILY_API_KEY not found.")
        return {"results": [], "images": []}
    
    try:
        client = TavilyClient()
        response = client.search(query, max_results=max_results, include_images=True)
        return {
            "results": response.get("results", []),
            "images": response.get("images", [])
        }
    except Exception as e:
        print(f"Search API Error: {e}")
        return {"results": [], "images": []}




RESEARCH_SYSTEM = """You are an expert Data Extraction and Fact-Verification Agent for a Biology AI.

Your job is to read raw, messy web search results and extract only the highest-quality scientific data into strict EvidenceItem objects.

RULES FOR EXTRACTION:
1. Quality Control: Ignore advertisements, opinion blogs, and irrelevant noise. Only extract data from authoritative sources (e.g., NCBI, PubMed, Nature, university websites).
2. Snippet Rewriting: Do not just copy-paste the raw messy HTML snippet. Rewrite the snippet into a dense, highly accurate academic summary of the biological fact found on that page.
3. Dates: Normalize the 'published_at' field to ISO YYYY-MM-DD format ONLY if a date is explicitly stated in the text. If no date is found, you MUST leave it null. Do NOT guess or hallucinate dates.
4. Strict Filtering: If a search result does not contain a valid, working URL, completely discard it.
5. Deduplication: If multiple search results point to the exact same URL, only extract it once. Combine the best information into a single EvidenceItem.
6. Images: You will be provided with a list of Image URLs from the search. Pick 1 to 3 of the best image URLs and assign them to the image_url field of the relevant EvidenceItem.

You are the final filter. Ensure the data you output is flawless so the writer agent can rely on it perfectly.
"""

async def research_node(state: State) -> dict:
    queries = state.get("queries", [])[:3]  
    raw_results: List[dict] = []
    all_images: List[str] = []

    for q in queries:
        search_data = tavily_search(q, max_results=3)  # cut from 6 → 3 per query
        raw_results.extend(search_data["results"])
        all_images.extend(search_data["images"])

    if not raw_results:
        return {"evidence": []}

    # Truncate each result's content before stringifying the whole list
    trimmed_results = [
        {**r, "content": r.get("content", "")[:500]}
        for r in raw_results
    ]

    extractor = llm.with_structured_output(EvidencePack)
    pack: EvidencePack = await extractor.ainvoke([
        SystemMessage(content=RESEARCH_SYSTEM),
        HumanMessage(content=(
            f"Topic: {state['topic']}\n"
            f"Raw results to clean:\n{trimmed_results}\n"
            f"Available Image URLs:\n{all_images[:10]}"
        ))
    ])
    # ... rest unchanged

    dedup = {}
    for e in pack.evidence:
        if e.url and e.url not in dedup:
            dedup[e.url] = e
            
    evidence = list(dedup.values())
    return {"evidence": evidence}