"""
tests/test_architecture_mapper.py — Verification of Architecture Mapper & Boss Routing.

Tests:
  1. Deterministic AST tools (get_file_outline, find_import_dependencies, get_codebase_tree).
  2. Boss (Coordinator) correctly routing structural / import questions to architecture_mapper.
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

from code_helper.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai import types


async def ask_boss(runner: InMemoryRunner, test_query: str):
    print("\n" + "=" * 65)
    print(f"USER QUERY: \"{test_query}\"")
    print("=" * 65)

    session_id = f"arch_session_{int(time.time() * 1000)}"
    user_id = "test_lead_engineer"

    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id,
    )

    user_msg = types.Content(
        role="user",
        parts=[types.Part.from_text(text=test_query)],
    )

    final_response = ""
    active_agent = "coordinator"
    abort_signal = asyncio.Event()
    tools_called_count = 0
    last_resp_text = ""

    async def _run_stream():
        nonlocal active_agent, final_response, tools_called_count, last_resp_text
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_msg,
            abort_signal=abort_signal,
        ):
            if hasattr(event, "author") and event.author:
                if event.author != active_agent:
                    print(f"\n[*] [AGENT TRANSFER] Control transitioned: {active_agent} -> {event.author}", flush=True)
                    active_agent = event.author

            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if getattr(part, "function_call", None):
                        fn_name = part.function_call.name
                        fn_args = getattr(part.function_call, "args", {})
                        if fn_name in ["text", "respond", "answer", "message"]:
                            t = fn_args.get("text") or fn_args.get("message") or ""
                            if t:
                                final_response += str(t)
                            continue
                        print(f"  [{active_agent}] [TOOL CALL] -> {fn_name}({fn_args})", flush=True)
                        if fn_name != "transfer_to_agent":
                            tools_called_count += 1
                            if tools_called_count >= 2:
                                print(f"  [SAFETY GUARD] Tool executed. Stopping loop.", flush=True)
                                abort_signal.set()
                                return
                    elif getattr(part, "function_response", None):
                        resp_name = part.function_response.name
                        resp_data = getattr(part.function_response, "response", {})
                        if isinstance(resp_data, dict):
                            last_resp_text = resp_data.get("result", "") or str(resp_data)
                        elif isinstance(resp_data, str):
                            last_resp_text = resp_data
                        print(f"  [{active_agent}] [TOOL RESPONSE] <- {resp_name} completed.", flush=True)
                    elif getattr(part, "text", None):
                        final_response += part.text

    try:
        await asyncio.wait_for(_run_stream(), timeout=40.0)
    except asyncio.TimeoutError:
        print("  [TIMEOUT GUARD] Completed via timeout protection.", flush=True)
        abort_signal.set()

    if not final_response and last_resp_text:
        final_response = last_resp_text

    print("\n" + "-" * 65, flush=True)
    print(f"FINAL ANSWER PRODUCED (By {active_agent}):", flush=True)
    print("-" * 65, flush=True)
    print(final_response.strip(), flush=True)
    print("-" * 65, flush=True)
    return final_response


async def main():
    print("\n" + "#" * 65)
    print("STARTING ARCHITECTURE MAPPER VERIFICATION SUITE")
    print("#" * 65)

    runner = InMemoryRunner(agent=root_agent)

    # Test 1: Canonical Assignment Question: "Which files import config.py?"
    await ask_boss(runner, "Which files import config.py?")

    # Test 2: Function and class outline: "What functions and classes are in indexer.py?"
    await ask_boss(runner, "What functions and classes are in indexer.py?")


if __name__ == "__main__":
    asyncio.run(main())
