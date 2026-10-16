"""
tests/test_code_searcher.py — Standalone Verification for Code Searcher Worker Agent.
"""
import asyncio
import os
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code_helper.config import config
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.genai import types
from code_helper.tools.search_tools import rag_search


def create_searcher_agent() -> LlmAgent:
    """Build the Code Searcher worker agent per Student Guide Page 5."""
    model = LiteLlm(model="nvidia_nim/meta/llama-3.2-11b-vision-instruct")
    
    searcher = LlmAgent(
        name="code_searcher",
        model=model,
        description="Finds where something is in the code.",
        instruction=(
            "Use your search tool to find code. "
            "Explain which file and lines implement the requested functionality based on the search results. "
            "If the search returns nothing useful or the functionality is absent from the codebase, say: 'I could not find that in the codebase.'"
        ),
        tools=[rag_search],
    )
    return searcher


async def ask_agent(runner: InMemoryRunner, user_query: str):
    print("\n" + "=" * 65)
    print(f"USER QUERY: \"{user_query}\"")
    print("=" * 65)

    session_id = f"session_{int(time.time() * 1000)}"
    user_id = "test_developer"

    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id,
    )

    user_msg = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_query)],
    )

    print("[*] Running Code Searcher agent loop...")
    final_response = ""

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_msg,
    ):
        if hasattr(event, "content") and event.content:
            for part in event.content.parts:
                if getattr(part, "function_call", None):
                    fn_name = part.function_call.name
                    fn_args = getattr(part.function_call, "args", {})
                    print(f"  [TOOL CALL] -> {fn_name}({fn_args})")
                elif getattr(part, "function_response", None):
                    resp_name = part.function_response.name
                    print(f"  [TOOL RESPONSE] <- {resp_name} completed.")
                elif getattr(part, "text", None):
                    final_response += part.text

    print("\n" + "-" * 65)
    print("AGENT FINAL ANSWER:")
    print("-" * 65)
    print(final_response.strip())
    print("-" * 65)
    return final_response


async def main():
    print("\n" + "#" * 65)
    print("STARTING CODE SEARCHER ISOLATION TEST (ADK + LITELLM + RAG TOOL)")
    print("#" * 65)

    agent = create_searcher_agent()
    runner = InMemoryRunner(agent=agent)

    # Test 1: Where is vector similarity search performed?
    await ask_agent(runner, "Where is vector similarity search performed in the code?")

    # Test 2: Negative query
    await ask_agent(runner, "Where is the Stripe payment billing webhook handled in the codebase?")


if __name__ == "__main__":
    asyncio.run(main())
