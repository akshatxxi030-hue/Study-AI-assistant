import asyncio
from dotenv import load_dotenv
load_dotenv()

from CORE.graph import app   # adjust import path to wherever you compiled `app = g.compile(...)`

async def run_test(topic: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    result = await app.ainvoke({"topic": topic}, config=config)
    print("\n--- RESULT ---")
    print(result)
    return result

async def main():
    # Test 1: should hit direct_answer (router only, no retrieval)
    print("=== TEST 1: Direct answer ===")
    await run_test("full form of RNA", thread_id="test-1")

    # Test 2: should hit local_database → CRAG path
    #print("\n=== TEST 2: Local database / CRAG ===")
    #await run_test("Explain the specific enzyme kinetics example from my textbook", thread_id="test-2")

    # Test 3: should hit web_search → Research agent
    #print("\n=== TEST 3: Web search / Research ===")
    #await run_test("What are the latest 2026 CRISPR clinical trial results?", thread_id="test-3")

if __name__ == "__main__":
    asyncio.run(main())