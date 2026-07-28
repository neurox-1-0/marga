import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

models_to_test = [
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
]

async def test_models():
    for m in models_to_test:
        try:
            llm = ChatGoogleGenerativeAI(model=m)
            res = await llm.ainvoke([HumanMessage(content="hello")])
            print(f"[SUCCESS] {m}: {res.content[:20]}")
        except Exception as e:
            print(f"[FAILED] {m}: {str(e)[:100]}")

if __name__ == "__main__":
    asyncio.run(test_models())
