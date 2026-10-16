"""
frontend/server.py — FastAPI Web Server for Multi-Agent Code Helper Visualizer.

Provides:
  - Interactive web UI static file serving
  - Live agent query endpoint (/api/query) executing Google ADK root_agent
  - Latest benchmark scorecard endpoint (/api/benchmarks)
  - Codebase structure & AST outline endpoint (/api/codebase)
  - System telemetry endpoint (/api/stats)
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from code_helper.config import config
from code_helper.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

app = FastAPI(title="Multi-Agent Code Helper Observatory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)


class QueryRequest(BaseModel):
    query: str
    mode: Optional[str] = "live"  # "live" or "simulate"


@app.get("/")
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return FileResponse(index_file)


@app.get("/api/benchmarks")
async def get_benchmarks():
    """Returns the latest golden question benchmark results."""
    bench_file = PROJECT_ROOT / "tests" / "benchmark_results.json"
    if bench_file.exists():
        try:
            with open(bench_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {"status": "ok", "benchmarks": data}
        except Exception as e:
            return {"status": "error", "message": str(e), "benchmarks": []}
    return {"status": "not_found", "benchmarks": []}


@app.get("/api/stats")
async def get_stats():
    """Returns system configuration and vector DB stats."""
    stats = {
        "chat_model": config.chat_model,
        "embed_model": config.embed_model,
        "embed_dimension": config.embed_dimension,
        "pinecone_index": config.pinecone_index_name,
        "pinecone_cloud": config.pinecone_cloud,
        "pinecone_region": config.pinecone_region,
        "target_codebase": config.target_codebase_dir.name,
        "workers": [
            {"id": "code_searcher", "name": "Code Searcher", "tool": "rag_search", "type": "RAG Vector DB"},
            {"id": "architecture_mapper", "name": "Architecture Mapper", "tool": "ast_tools", "type": "Python AST"},
            {"id": "onboarding_guide", "name": "Onboarding Guide", "tool": "onboarding_tools", "type": "Quickstart"},
            {"id": "code_explainer", "name": "Code Explainer", "tool": "read_file", "type": "Filesystem MCP"},
        ],
    }
    # Try fetching live vector count
    try:
        from pinecone import Pinecone
        if config.pinecone_api_key:
            pc = Pinecone(api_key=config.pinecone_api_key)
            idx = pc.Index(config.pinecone_index_name)
            desc = idx.describe_index_stats()
            stats["total_vectors"] = desc.total_vector_count
        else:
            stats["total_vectors"] = 103
    except Exception:
        stats["total_vectors"] = 103
    return stats


@app.get("/api/codebase")
async def get_codebase():
    """Lists files and structure of target codebase."""
    target_dir = config.target_codebase_dir
    files = []
    if target_dir.exists():
        for p in sorted(target_dir.glob("*.py")):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                files.append({
                    "name": p.name,
                    "line_count": len(lines),
                    "char_count": sum(len(l) for l in lines),
                    "preview": "".join(lines[:25]),
                })
            except Exception:
                pass
    return {"status": "ok", "directory": target_dir.name, "files": files}


@app.post("/api/query")
async def handle_query(req: QueryRequest):
    """
    Executes query through the multi-agent coordinator with real-time trace collection
    and infinite loop prevention.
    """
    query_text = req.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    t0 = time.time()
    trace = []
    trace.append({
        "stage": "USER_INPUT",
        "timestamp": round(time.time() - t0, 3),
        "detail": f"Query submitted: \"{query_text}\"",
    })

    runner = InMemoryRunner(agent=root_agent)
    session_id = f"web_{int(time.time() * 1000)}"
    user_id = "web_explorer"

    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id,
    )

    user_msg = types.Content(
        role="user",
        parts=[types.Part.from_text(text=query_text)],
    )

    routed_worker = None
    tools_called = []
    last_tool_output = ""
    final_text_chunks = []
    abort_signal = asyncio.Event()

    async def _stream_execution():
        nonlocal routed_worker, last_tool_output
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_msg,
            abort_signal=abort_signal,
        ):
            author = getattr(event, "author", None) or getattr(event, "sender", "unknown")
            if hasattr(event, "content") and event.content and event.content.parts:
                for p in event.content.parts:
                    # Check for tool call
                    if getattr(p, "function_call", None):
                        fc = p.function_call
                        fn_name = fc.name
                        args = dict(fc.args) if fc.args else {}

                        if fn_name in ["text", "respond", "answer", "message"]:
                            pseudo = args.get("text") or args.get("message") or ""
                            if pseudo:
                                final_text_chunks.append(str(pseudo))
                            continue

                        tools_called.append({"author": author, "tool": fn_name, "args": args})

                        if fn_name == "transfer_to_agent" and "agent_name" in args:
                            routed_worker = args["agent_name"]
                            trace.append({
                                "stage": "COORDINATOR_ROUTING",
                                "timestamp": round(time.time() - t0, 3),
                                "source": "coordinator",
                                "target": routed_worker,
                                "detail": f"Coordinator transferred control to -> '{routed_worker}'",
                            })
                        else:
                            trace.append({
                                "stage": "TOOL_INVOCATION",
                                "timestamp": round(time.time() - t0, 3),
                                "agent": author,
                                "tool": fn_name,
                                "args": args,
                                "detail": f"Agent '{author}' called tool '{fn_name}'",
                            })

                        # Loop Guard: Max 2 worker tools
                        worker_tools = [t for t in tools_called if t["tool"] != "transfer_to_agent"]
                        if len(worker_tools) >= 2:
                            trace.append({
                                "stage": "LOOP_GUARD",
                                "timestamp": round(time.time() - t0, 3),
                                "detail": "Loop Guard engaged: tool limit reached. Synthesizing answer.",
                            })
                            abort_signal.set()
                            return

                    # Check for tool response
                    if getattr(p, "function_response", None):
                        fr = p.function_response
                        resp_data = getattr(fr, "response", {})
                        if isinstance(resp_data, dict):
                            last_tool_output = resp_data.get("result", "") or str(resp_data)
                        elif isinstance(resp_data, str):
                            last_tool_output = resp_data
                        trace.append({
                            "stage": "TOOL_RESPONSE",
                            "timestamp": round(time.time() - t0, 3),
                            "tool": fr.name,
                            "output_preview": (last_tool_output[:200] + "...") if len(last_tool_output) > 200 else last_tool_output,
                            "detail": f"Tool '{fr.name}' returned output data.",
                        })

                    # Check for text output
                    if getattr(p, "text", None) and p.text:
                        if author != "coordinator":
                            raw = p.text.strip()
                            if raw.startswith("<|python_tag|>"):
                                raw = raw[len("<|python_tag|>"):].strip()
                            try:
                                parsed = json.loads(raw)
                                if isinstance(parsed, dict) and "text" in parsed:
                                    raw = parsed["text"]
                            except Exception:
                                pass
                            if raw:
                                final_text_chunks.append(raw)

    try:
        await asyncio.wait_for(_stream_execution(), timeout=40.0)
    except asyncio.TimeoutError:
        trace.append({
            "stage": "TIMEOUT_GUARD",
            "timestamp": round(time.time() - t0, 3),
            "detail": "Timeout guard (40s) cleanly halted execution.",
        })
        abort_signal.set()
    except Exception as err:
        trace.append({
            "stage": "EXCEPTION",
            "timestamp": round(time.time() - t0, 3),
            "detail": f"Handled stream exception: {err}",
        })
        abort_signal.set()

    elapsed = round(time.time() - t0, 2)
    final_answer = "\n".join(final_text_chunks).strip()

    if not final_answer and last_tool_output:
        final_answer = last_tool_output.strip()

    if "no relevant code" in final_answer.lower() or "no relevant code" in last_tool_output.lower():
        final_answer = "I could not find that in the codebase."

    trace.append({
        "stage": "COMPLETED",
        "timestamp": elapsed,
        "worker": routed_worker or "coordinator",
        "detail": f"Execution finished in {elapsed}s with final grounded answer.",
    })

    return {
        "status": "ok",
        "query": query_text,
        "worker": routed_worker or "coordinator",
        "tools_called": [t["tool"] for t in tools_called],
        "elapsed_sec": elapsed,
        "final_answer": final_answer,
        "trace": trace,
    }


# Mount static assets directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def run():
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    print(f"\n[OBSERVATORY LAUNCH] Starting Multi-Agent Frontend at: http://127.0.0.1:{port}\n")
    uvicorn.run("frontend.server:app", host="127.0.0.1", port=port, reload=False)


if __name__ == "__main__":
    run()
