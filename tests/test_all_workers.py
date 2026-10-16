"""
tests/test_all_workers.py — Multi-Agent Routing & Execution Benchmark.

Tests the full 4-worker team orchestrated by the Coordinator (Boss):
  - Q1 (Searcher) : "Where is document chunking implemented in the code?"
  - Q2 (Mapper)   : "Which files import config.py?"
  - Q3 (Guide)    : "I am new to this project. Where do I start?"
  - Q4 (Explainer): "Explain vector_store.py in detail."
"""
import asyncio
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code_helper.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai import types


async def ask_coordinator(runner: InMemoryRunner, test_query: str):
    print("\n" + "=" * 70)
    print(f"USER QUERY: \"{test_query}\"")
    print("=" * 70)

    session_id = f"bench_session_{int(time.time() * 1000)}"
    user_id = "bench_developer"

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
    worker_tools_count = 0
    last_tool_res = ""

    async def _run_stream():
        nonlocal active_agent, final_response, worker_tools_count, last_tool_res
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_msg,
            abort_signal=abort_signal,
        ):
            if hasattr(event, "author") and event.author:
                if event.author != active_agent:
                    print(f"[*] [TRANSFER] {active_agent} -> {event.author}", flush=True)
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
                            worker_tools_count += 1
                            if worker_tools_count >= 2:
                                print(f"  [SAFETY GUARD] Tool executed. Stopping loop.", flush=True)
                                abort_signal.set()
                                return
                    elif getattr(part, "function_response", None):
                        resp_name = part.function_response.name
                        resp_data = getattr(part.function_response, "response", {})
                        if isinstance(resp_data, dict):
                            last_tool_res = resp_data.get("result", "") or str(resp_data)
                        elif isinstance(resp_data, str):
                            last_tool_res = resp_data
                        print(f"  [{active_agent}] [TOOL RESPONSE] <- {resp_name} completed.", flush=True)
                    elif getattr(part, "text", None):
                        final_response += part.text

    try:
        await asyncio.wait_for(_run_stream(), timeout=45.0)
    except asyncio.TimeoutError:
        print("  [TIMEOUT GUARD] Terminated via 45s safety guard.", flush=True)
        abort_signal.set()

    if not final_response and last_tool_res:
        final_response = last_tool_res

    print("-" * 70, flush=True)
    print(f"RESPONSE FROM [{active_agent}]:", flush=True)
    print("-" * 70, flush=True)
    print(final_response.strip(), flush=True)
    print("-" * 70, flush=True)
    return active_agent, final_response


async def main():
    print("\n" + "#" * 70)
    print("MULTI-AGENT BENCHMARK SUITE: 1 BOSS + 4 WORKERS")
    print("#" * 70)

    runner = InMemoryRunner(agent=root_agent)

    # 1. Onboarding Guide Test
    await ask_coordinator(runner, "I am new to this project. Where do I start?")

    # 2. Architecture Mapper Test
    await ask_coordinator(runner, "Which files import config.py?")

    # 3. Code Explainer Test
    await ask_coordinator(runner, "Explain vector_store.py in detail.")


if __name__ == "__main__":
    asyncio.run(main())
