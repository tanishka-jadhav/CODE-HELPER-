"""
code_helper/agent.py — Multi-Agent Code Helper root coordinator and worker wiring.

Built strictly per Student Guide Section 4, 5, 6, 7 & 8:
  1 Boss: coordinator (Never answers yourself. Pick the best worker.)
  4 Workers:
    - code_searcher (Finds where something is in the code.)
    - code_explainer (Reads a whole file and explains it. Uses MCP server.)
    - architecture_mapper (Lists files, functions and imports with plain Python. No AI guessing.)
    - onboarding_guide (Says what the project does, how to run it, and where to start.)
"""
import shutil
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from code_helper.config import config
from code_helper.tools.search_tools import rag_search
from code_helper.tools.ast_tools import (
    get_file_outline,
    find_import_dependencies,
    get_codebase_tree,
)
from code_helper.tools.onboarding_tools import get_project_quickstart_and_modules

# Shared Model Instance (NVIDIA NIM via LiteLLM)
model = LiteLlm(
    model=f"nvidia_nim/{config.chat_model}",
    api_key=config.nvidia_api_key,
)

# =====================================================================
# MCP FILESYSTEM TOOLSET (For Code Explainer)
# Student Guide Section 6 & 8: @modelcontextprotocol/server-filesystem
# =====================================================================
npx_binary = shutil.which("npx") or "npx"
target_codebase_str = str(config.target_codebase_dir.resolve().as_posix())

file_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=npx_binary,
            args=["-y", "@modelcontextprotocol/server-filesystem", target_codebase_str],
        ),
        timeout=30,
    ),
    tool_filter=["list_directory", "read_file"],
)

# =====================================================================
# WORKER 1: Code Searcher (Finds where something is)
# =====================================================================
searcher = LlmAgent(
    name="code_searcher",
    model=model,
    description="Finds where specific features or logic are implemented in the code using RAG search.",
    instruction=(
        "You are the code_searcher worker. Call rag_search EXACTLY ONCE with the search query.\n"
        "As soon as rag_search returns results, review them and answer the user directly:\n"
        "- State the file name, line numbers, and code snippet where the logic is implemented.\n"
        "- ONLY if rag_search explicitly returns 'No relevant code passages found', reply: 'I could not find that in the codebase.'\n"
        "- DO NOT call rag_search again. Provide your final answer immediately."
    ),
    tools=[rag_search],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

# =====================================================================
# WORKER 2: Code Explainer (Reads a whole file and explains it)
# =====================================================================
explainer = LlmAgent(
    name="code_explainer",
    model=model,
    description="Reads a whole file and explains its architecture, logic, and implementation in detail using filesystem MCP.",
    instruction=(
        "You are the code_explainer worker. Call read_file with the requested file path (e.g. 'vector_store.py').\n"
        "As soon as read_file returns the file content, explain the file thoroughly: classes, functions, and workflow.\n"
        "- DO NOT call tools repeatedly. Deliver your final answer directly to the user."
    ),
    tools=[file_tools],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

# =====================================================================
# WORKER 3: Architecture Mapper (Lists files, functions and imports with plain Python)
# =====================================================================
mapper = LlmAgent(
    name="architecture_mapper",
    model=model,
    description="Analyzes imports, dependencies, function/class outlines, and file structure using deterministic Python AST tools.",
    instruction=(
        "You are the architecture_mapper worker.\n"
        "STRICT EXECUTION PROTOCOL:\n"
        "1. Select and execute EXACTLY ONE tool that corresponds to the user's inquiry:\n"
        "   - Which files import a module: call find_import_dependencies ONLY.\n"
        "   - Outline of classes/functions in a file: call get_file_outline ONLY.\n"
        "   - File tree / directory structure: call get_codebase_tree ONLY.\n"
        "2. Do NOT call more than one tool. If you called find_import_dependencies, do NOT call get_file_outline or get_codebase_tree.\n"
        "3. Once the tool returns, IMMEDIATELY formulate your final answer in text and output it directly to the user.\n"
        "4. DO NOT issue any further tool calls under any circumstances."
    ),
    tools=[find_import_dependencies, get_file_outline, get_codebase_tree],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

# =====================================================================
# WORKER 4: Onboarding Guide (Says what the project does, how to run it, where to start)
# =====================================================================
guide = LlmAgent(
    name="onboarding_guide",
    model=model,
    description="Guides new developers by providing project overview, module summaries, and execution quickstart.",
    instruction=(
        "You are the onboarding_guide worker. Call get_project_quickstart_and_modules EXACTLY ONCE.\n"
        "As soon as the tool returns the guide, explain to the user what the project does, the recommended reading order, and how to run it.\n"
        "You must deliver your final answer directly to the user."
    ),
    tools=[get_project_quickstart_and_modules],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

# =====================================================================
# COORDINATOR ("BOSS") AGENT
# Invariant: Never answers yourself. Pick the best worker.
# =====================================================================
root_agent = LlmAgent(
    name="coordinator",
    model=model,
    description="Sends each question to the right worker.",
    instruction=(
        "You are the coordinator boss. You NEVER answer technical or codebase questions yourself.\n"
        "You MUST immediately transfer to exactly one worker agent using transfer_to_agent:\n"
        "- If the user asks where something is located, where logic is implemented, or to search code: transfer to 'code_searcher'.\n"
        "- If the user asks to explain a file or what a file does in detail: transfer to 'code_explainer'.\n"
        "- If the user asks about imports, dependencies, AST outlines, functions in a file, or directory tree: transfer to 'architecture_mapper'.\n"
        "- If the user asks where to start, what the project does, how to run it, or onboarding overview: transfer to 'onboarding_guide'.\n"
        "Never reply directly with an answer. Always call transfer_to_agent immediately."
    ),
    sub_agents=[searcher, explainer, mapper, guide],
)

