<div align="center">

# 🤖 Multi-Agent Code Helper

### *An Autonomous Hierarchical Multi-Agent System for Intelligent Codebase Exploration & Architectural Comprehension*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-Agent%20Framework-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://github.com/google/adk)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA%20NIM-Llama--3.2--11B-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://build.nvidia.com)
[![Pinecone](https://img.shields.io/badge/Pinecone-Serverless%20VectorDB-000000?style=for-the-badge&logo=pinecone&logoColor=white)](https://www.pinecone.io)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Filesystem%20Server-FF6C37?style=for-the-badge&logo=json&logoColor=white)](https://modelcontextprotocol.io)
[![Benchmark](https://img.shields.io/badge/Evaluation-5%2F5%20Golden%20Tests%20Passed-success?style=for-the-badge&logo=checkmarx&logoColor=white)](https://github.com/tanishka-jadhav/CODE-HELPER-)

<p align="center">
  <a href="#-executive-summary">Executive Summary</a> •
  <a href="#-multi-agent-team-architecture">Agent Architecture</a> •
  <a href="#-tools-catalog">Tools Catalog</a> •
  <a href="#-manual-5-step-rag-pipeline">5-Step RAG</a> •
  <a href="#-chunking-strategy--empirical-analysis">Chunking Strategy</a> •
  <a href="#-model-context-protocol-mcp">MCP Integration</a> •
  <a href="#-quickstart--execution-guide">Quickstart</a> •
  <a href="#-golden-evaluation-showcase">Benchmarks</a> •
  <a href="#-engineering-challenges--fixes">Engineering Fixes</a>
</p>

</div>

---

## 📖 Table of Contents
1. [🌟 Executive Summary](#-executive-summary)
2. [🏛️ Multi-Agent Team Architecture](#️-multi-agent-team-architecture)
3. [🛠️ Comprehensive Tools Catalog](#️-comprehensive-tools-catalog)
4. [🔍 Manual 5-Step RAG Pipeline](#-manual-5-step-rag-pipeline)
5. [⚖️ Chunking Strategy & Empirical Analysis](#️-chunking-strategy--empirical-analysis)
6. [🔌 Model Context Protocol (MCP) Integration](#-model-context-protocol-mcp-integration)
7. [📁 Repository Layout](#-repository-layout)
8. [🚀 Quickstart & Execution Guide](#-quickstart--execution-guide)
9. [📊 Golden Evaluation Showcase (Benchmark Results)](#-golden-evaluation-showcase)
10. [🛡️ Engineering Challenges & Production Fixes](#️-engineering-challenges--production-fixes)
11. [✅ Student Guide Compliance Checklist](#-student-guide-compliance-checklist)

---

## 🌟 Executive Summary

**Multi-Agent Code Helper** is an intelligent developer assistant designed to onboard engineers and navigate Python codebases with high factual accuracy. Built using the **Google Agent Development Kit (ADK)**, **NVIDIA NIM** (via **LiteLLM**), and **Pinecone Serverless**, the system employs a disciplined hierarchy of **1 Coordinator Boss** and **4 specialized Worker agents** that handle code search, full-file explanation, structural dependency mapping, and newcomer orientation. Rather than relying on LLM guesswork, the team combines a manual 5-step semantic RAG engine, Model Context Protocol (MCP) sandboxed file access, and deterministic Python Abstract Syntax Tree (AST) analysis.

---

## 🏛️ System Architecture & Multi-Agent Design

The Multi-Agent Code Helper is engineered using a **tiered, service-oriented multi-agent architecture** managed by the **Google Agent Development Kit (ADK)**. 

### Multi-Tier Architecture Diagram

```mermaid
graph TD
    %% Tier 1: Client Interfaces
    subgraph TIER_CLIENT ["🖥️ Tier 1: Presentation & Client Interfaces"]
        CLI["ADK CLI Terminal<br/><code>adk run code_helper</code>"]
        WEB["ADK Web Dashboard<br/><code>adk web</code>"]
        OBS["Observatory Dashboard<br/><code>http://127.0.0.1:8080</code>"]
    end

    %% Tier 2: Coordinator & Gateway
    subgraph TIER_ROUTING ["👑 Tier 2: Orchestration & Intelligent Routing"]
        BOSS["Coordinator Boss Agent<br/>(LlmAgent root_agent)"]
        LITELLM["LiteLLM Universal Gateway<br/>(NVIDIA NIM Translation)"]
        ROUTER["Intent Evaluator & Triage<br/>(transfer_to_agent)"]
    end

    %% Tier 3: Specialized Workers
    subgraph TIER_WORKERS ["⚙️ Tier 3: Autonomous Specialist Workers"]
        W_SEARCH["🔍 Code Searcher<br/>(Semantic Code Locator)"]
        W_EXPLAIN["📖 Code Explainer<br/>(Whole-File Architecture)"]
        W_MAPPER["📐 Architecture Mapper<br/>(AST Dependency Engine)"]
        W_GUIDE["🧭 Onboarding Guide<br/>(Newcomer Orientation)"]
    end

    %% Tier 4: Tool Execution Engines
    subgraph TIER_TOOLS ["🛠️ Tier 4: Execution & Tool Engines"]
        T_RAG["rag_search()<br/>Query Embedding & Cosine KNN"]
        T_MCP["McpToolset Client<br/>Stdio JSON-RPC Protocol"]
        T_AST["Python AST Engine<br/>ast.parse & Node Visitor"]
        T_GUIDE["Onboarding Spec Tool<br/>Module Roadmap & Run Guide"]
    end

    %% Tier 5: External Services & Storage
    subgraph TIER_INFRA ["☁️ Tier 5: External Services & Storage"]
        NVIDIA_LLM["NVIDIA NIM Chat API<br/>meta/llama-3.2-11b-vision-instruct"]
        NVIDIA_EMBED["NVIDIA NIM Embeddings<br/>nvidia/nemotron-3-embed-1b (2048-dim)"]
        PINECONE["Pinecone Serverless DB<br/>code-helper (AWS us-east-1, Cosine)"]
        MCP_SERVER["Node.js MCP Filesystem Server<br/>@modelcontextprotocol/server-filesystem"]
        TARGET_CODE["Target Codebase Disk<br/>Naive_RAG/*.py"]
    end

    %% Cross-Tier Connections
    CLI --> BOSS
    WEB --> BOSS
    OBS --> BOSS

    BOSS --> LITELLM
    LITELLM --> NVIDIA_LLM
    BOSS --> ROUTER

    ROUTER -->|Where is code / logic?| W_SEARCH
    ROUTER -->|Explain whole file?| W_EXPLAIN
    ROUTER -->|Imports / dependencies?| W_MAPPER
    ROUTER -->|Where to start / overview?| W_GUIDE

    W_SEARCH --> T_RAG
    W_EXPLAIN --> T_MCP
    W_MAPPER --> T_AST
    W_GUIDE --> T_GUIDE

    T_RAG --> NVIDIA_EMBED
    T_RAG --> PINECONE
    T_MCP --> MCP_SERVER
    MCP_SERVER --> TARGET_CODE
    T_AST --> TARGET_CODE
    T_GUIDE --> TARGET_CODE

    classDef client fill:#1E293B,stroke:#38BDF8,stroke-width:1.5px,color:#FFFFFF;
    classDef boss fill:#312E81,stroke:#818CF8,stroke-width:2px,color:#FFFFFF;
    classDef worker fill:#0F172A,stroke:#A855F7,stroke-width:1.5px,color:#E2E8F0;
    classDef tool fill:#14532D,stroke:#4ADE80,stroke-width:1.5px,color:#F0FDF4;
    classDef infra fill:#1C1917,stroke:#F59E0B,stroke-width:1.5px,color:#FEF3C7;

    class CLI,WEB,OBS client;
    class BOSS,LITELLM,ROUTER boss;
    class W_SEARCH,W_EXPLAIN,W_MAPPER,W_GUIDE worker;
    class T_RAG,T_MCP,T_AST,T_GUIDE tool;
    class NVIDIA_LLM,NVIDIA_EMBED,PINECONE,MCP_SERVER,TARGET_CODE infra;
```

### Architectural Principles & Layer Breakdown

1. **Presentation Tier (Multi-Channel Interface)**:
   - **ADK Terminal Runner (`adk run code_helper`)**: Direct stdin/stdout CLI REPL for developers.
   - **ADK Web UI (`adk web`)**: Official Google session-graph visualizer on port 8000.
   - **Observatory Dashboard (`frontend/server.py`)**: Custom real-time visual flight simulator and chat interface on port 8080.

2. **Orchestration Tier (The Coordinator Boss)**:
   - **Invariant**: The Boss **never** answers technical questions directly.
   - **Triage Protocol**: Parses query semantics and invokes Google ADK's built-in `transfer_to_agent` mechanism to delegate control to exactly one worker.
   - **Shared Model Connection**: Uses a unified `LiteLlm` client pointing to NVIDIA NIM (`meta/llama-3.2-11b-vision-instruct`).

3. **Specialized Worker Tier**:
   - Each worker operates as a bounded agent with a dedicated instruction set.
   - **Agent Isolation**: Configured with `disallow_transfer_to_parent=True` and `disallow_transfer_to_peers=True` to prevent infinite delegation loops and ensure deterministic completion.

4. **Tool & Engine Tier**:
   - **Custom RAG Engine (`rag_search`)**: 5-step manual retrieval pipeline with a 0.72 similarity threshold and keyword validation guard.
   - **Deterministic AST Parser (`find_import_dependencies`, `get_file_outline`)**: Uses Python's native `ast` module to read language grammar with 100% mathematical accuracy. Zero LLM guessing.
   - **Model Context Protocol Client (`file_tools`)**: Bridges the agent to the official `@modelcontextprotocol/server-filesystem` JSON-RPC stdio daemon.

5. **Persistence & Inference Tier**:
   - **Inference**: High-throughput inference via NVIDIA NIM REST endpoints.
   - **Vector Database**: Pinecone Serverless running on AWS `us-east-1` with 2048-dimensional vectors using the cosine similarity metric.
   - **Sandboxed Filesystem**: Read-only directory scoping strictly limited to the `Naive_RAG/` target codebase folder.

### Table of Agents

| Agent Name | Architectural Role | Assigned Tools | Example User Inquiries | Routing Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **`coordinator`** | **Coordinator (Boss)** | `transfer_to_agent` | *"Any incoming question"* | Evaluates query semantics; delegates to one worker. Never generates direct answers. |
| **`code_searcher`** | **Specialized Worker** | `rag_search` | *"Where is document chunking implemented?"*<br/>*"Where are vectors normalized?"* | Targeted when user asks where specific functions, classes, or logic reside. |
| **`code_explainer`** | **Specialized Worker** | `read_file`, `list_directory` *(Filesystem MCP)* | *"Explain vector_store.py in detail."*<br/>*"Walk me through query_pipeline.py."* | Targeted when user asks to explain a whole file, module architecture, or script flow. |
| **`architecture_mapper`** | **Specialized Worker** | `find_import_dependencies`<br/>`get_file_outline`<br/>`get_codebase_tree` | *"Which files import config.py?"*<br/>*"Give me an outline of indexer.py."* | Targeted when user asks about imports, dependencies, AST outlines, or repository structure. |
| **`onboarding_guide`** | **Specialized Worker** | `get_project_quickstart_and_modules` | *"I am new to this project. Where do I start?"*<br/>*"How do I run this repo?"* | Targeted when user asks for getting-started orientation, reading orders, or overview commands. |

---


## 🛠️ Comprehensive Tools Catalog

Per assignment specifications:
- ✅ **At least 5 custom tools are built** (6 custom tools total, excluding MCP server built-in tools).
- ✅ **At least one tool uses no AI** (4 tools run plain deterministic Python).
- ✅ **Filesystem MCP server tools do not count toward the custom 5.**

| Tool Function | Implementation Engine | Technology | AI vs Plain Python | Worker Owner | Purpose & Output Contract |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **`rag_search`** | NVIDIA NIM + Pinecone | `openai`, `pinecone` | **AI** (Vectors) | `code_searcher` | Converts queries to 2048-d vectors via `nvidia/nemotron-3-embed-1b`, retrieves top-k chunks from Pinecone, checks keyword grounding, and formats output with file paths and line ranges. |
| **`find_import_dependencies`** | Python Syntax Tree | `ast` standard lib | **Plain Python (No AI)** | `architecture_mapper` | Statically parses AST `Import` and `ImportFrom` nodes across every `.py` file to locate exact dependencies and line numbers. Zero hallucination. |
| **`get_file_outline`** | Python Syntax Tree | `ast` standard lib | **Plain Python (No AI)** | `architecture_mapper` | Extracts class definitions, methods, functions, and their line ranges from source code. |
| **`get_codebase_tree`** | Filesystem Traversal | `pathlib` standard lib | **Plain Python (No AI)** | `architecture_mapper` | Statically scans and lists all tracked Python files in the target codebase. |
| **`get_project_quickstart_and_modules`** | Curated Knowledge Base | Standard Python | **Plain Python (No AI)** | `onboarding_guide` | Delivers the recommended reading sequence, purpose of each module, and CLI invocation commands. |
| **`read_code_file`** | Sandboxed IO Reader | `pathlib`, `io` | **Plain Python (No AI)** | Standalone / Offline | Direct sandboxed full-file reader with line numbers used for offline verification before MCP integration. |
| **`read_file`** *(MCP)* | Stdio JSON-RPC | `@modelcontextprotocol/server-filesystem` | **MCP Protocol** | `code_explainer` | Reads full, unchunked source files through the official Model Context Protocol server. |
| **`list_directory`** *(MCP)* | Stdio JSON-RPC | `@modelcontextprotocol/server-filesystem` | **MCP Protocol** | `code_explainer` | Lists directory contents through the official Model Context Protocol server. |

---

## 🔍 Manual 5-Step RAG Pipeline

Built entirely from scratch in `code_helper/index_codebase.py` and `code_helper/tools/search_tools.py` **without LangChain or LlamaIndex**:

```
[Target Codebase: Naive_RAG/*.py]
           │
           ▼
    ┌──────────────┐
    │ 1. READ      │  Scans Naive_RAG/*.py with UTF-8, capturing char & line counts
    └──────┬───────┘
           ▼
    ┌──────────────┐
    │ 2. SPLIT     │  Sliding window chunking (500 chars / 100 overlap) with exact line tracking
    └──────┬───────┘
           ▼
    ┌──────────────┐
    │ 3. EMBED     │  Batched embeddings via NVIDIA NIM (nvidia/nemotron-3-embed-1b, 2048 dims)
    └──────┬───────┘
           ▼
    ┌──────────────┐
    │ 4. STORE     │  Batch upsert to Pinecone Serverless (AWS us-east-1, Cosine Metric)
    └──────┬───────┘
           ▼
    ┌──────────────┐
    │ 5. SEARCH    │  Query embedding -> Pinecone top-k retrieval -> Keyword Grounding Guard
    └──────────────┘
```

1. **Step 1: Read (`read_codebase`)**: Traverses `Naive_RAG/` and reads every Python file (`config.py`, `indexer.py`, `vector_store.py`, `query_pipeline.py`, `main.py`).
2. **Step 2: Split (`split_into_chunks`)**: Slices files using a 500-character sliding window with 100-character overlap. Calculates exact source `start_line` and `end_line` for each chunk using newline offset tables.
3. **Step 3: Embed (`embed_chunks`)**: Transmits chunks in batches of 16 to NVIDIA NIM using the `nvidia/nemotron-3-embed-1b` model, generating 2048-dimensional dense vectors.
4. **Step 4: Store (`store_in_pinecone`)**: Batches and upserts records to Pinecone Serverless index (`code-helper`) on AWS `us-east-1`, persisting chunk text and line provenance in vector metadata.
5. **Step 5: Search (`rag_search`)**: Dynamically embeds user queries, calculates cosine nearest neighbors in Pinecone, filters results with grounding guards, and presents the relevant code snippets with line numbers.

---

## ⚖️ Chunking Strategy & Empirical Analysis

The chunking mechanism uses a **character-level sliding window** with exact line-boundary mapping.

* **Production Parameters**:
  * **Chunk Size**: `500` characters
  * **Chunk Overlap**: `100` characters
  * **Step / Stride**: `400` characters

### Empirical Comparison of Chunk Sizes

| Chunk Configuration | Semantic Precision | Context Completeness | Noise Level | Assessment for Python Codebase |
| :--- | :---: | :---: | :---: | :--- |
| **Small** *(200 chars / 40 overlap)* | ⚠️ Low | ❌ Poor | Low | **Under-chunking**: Frequently splits class/function headers from their logic or cuts docstrings in half. Fragments lack standalone semantic meaning. |
| **Large** *(1500 chars / 300 overlap)* | ⚠️ Low | ✅ High | ❌ High | **Over-chunking**: Combines 2 to 3 unrelated functions into a single embedding vector. Dilutes cosine similarity scores and injects irrelevant code into the LLM context. |
| **Selected** *(500 chars / 100 overlap)* | ✅ **High** | ✅ **Optimal** | ✅ **Minimal** | **Optimal Sweet Spot**: Matches the typical length of a Python function, class header, or docstring block in `Naive_RAG`. The 100-character overlap prevents boundary truncation. |

---

## 🔌 Model Context Protocol (MCP) Integration

The **Code Explainer** agent utilizes the **Model Context Protocol (MCP)** via `@modelcontextprotocol/server-filesystem` executed by `npx`.

```python
# code_helper/agent.py
file_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=shutil.which("npx") or "npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", target_codebase_str],
        ),
        timeout=30,
    ),
    tool_filter=["list_directory", "read_file"],
)
```

### Why MCP Was Chosen
- **Industry Standard**: MCP is the open standard protocol for bidirectional tool communication with language models over JSON-RPC stdio.
- **Sandboxed Security**: Rather than allowing unrestricted filesystem operations across the host OS, the MCP server is launched with a directory scope strictly restricted to the `Naive_RAG/` codebase folder.
- **Unchunked Holistic Context**: While RAG is optimal for pinpointing functions, code explanation requires reviewing full files end-to-end. MCP enables the agent to fetch complete source files on-demand.

---

## 📁 Repository Layout

```
DEBO ASSIGNMENT 2/
├── .env                              <- API keys and secrets (Never committed; in .gitignore)
├── .env.example                      <- Environment template for quick setup
├── .gitignore                        <- Ignores .env, virtual environments, caches
├── README.md                         <- Comprehensive project documentation
├── requirements.txt                  <- Dependencies: google-adk, litellm, pinecone, mcp, openai
│
├── code_helper/                      <- Main ADK Multi-Agent Package
│   ├── __init__.py                   <- Package entry point; environment sync
│   ├── agent.py                      <- Coordinator Boss & 4 Worker definitions
│   ├── config.py                     <- Centralized configuration container
│   ├── index_codebase.py             <- Offline 5-stage RAG indexer (Pinecone)
│   └── tools/                        <- Custom tools
│       ├── __init__.py               <- Exports tool functions
│       ├── ast_tools.py              <- Plain Python AST tools (dependencies, outlines)
│       ├── file_tools.py             <- Sandboxed direct file reader
│       ├── onboarding_tools.py       <- New developer quickstart & reading order
│       └── search_tools.py           <- RAG search tool with Pinecone & NVIDIA NIM
│
├── Naive_RAG/                        <- Target Python codebase being analyzed
│   ├── config.py                     <- Target codebase settings
│   ├── indexer.py                    <- Target codebase indexing logic
│   ├── main.py                       <- Target codebase entry point
│   ├── query_pipeline.py             <- Target codebase query pipeline
│   └── vector_store.py               <- Target codebase vector storage
│
├── frontend/                         <- Multi-Agent Observatory Web UI
│   ├── server.py                     <- FastAPI server for agent interaction & telemetry
│   └── static/                       <- Modern dark-mode web application (HTML/CSS/JS)
│
└── tests/                            <- Verification & Benchmark Suites
    ├── benchmark_results.json        <- Golden evaluation benchmark recordings
    ├── test_all_workers.py           <- Unit tests for each worker agent
    ├── test_architecture_mapper.py   <- AST parsing and dependency mapping tests
    ├── test_boss_routing.py          <- Coordinator routing logic tests
    ├── test_code_searcher.py         <- RAG retrieval tests
    ├── test_embeddings.py            <- NVIDIA NIM embedding connectivity tests
    ├── test_full_system.py           <- End-to-end integration tests
    ├── test_golden_questions.py      <- Canonical 5-question automated evaluation runner
    ├── test_mcp.py                   <- Filesystem MCP server connectivity tests
    ├── test_pinecone.py              <- Pinecone Serverless connection & upsert tests
    └── test_retrieval.py             <- Semantic similarity validation tests
```

---

## 🚀 Quickstart & Execution Guide

### Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: v18+ installed (`node -v` to verify)
- **NVIDIA NIM API Key**: Obtain from [build.nvidia.com](https://build.nvidia.com)
- **Pinecone API Key**: Obtain from [pinecone.io](https://www.pinecone.io)

### 1. Installation
```powershell
# Clone the repository
git clone https://github.com/tanishka-jadhav/CODE-HELPER-.git
cd "CODE-HELPER-"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials
Copy the example file to `.env`:
```powershell
Copy-Item .env.example .env
```
Edit `.env` with your API keys:
```env
NVIDIA_API_KEY=nvapi-your-key-here
NVIDIA_NIM_API_KEY=nvapi-your-key-here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_CHAT_MODEL=meta/llama-3.2-11b-vision-instruct
NVIDIA_EMBED_MODEL=nvidia/nemotron-3-embed-1b

PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=code-helper
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

PYTHONUTF8=1
```

### 3. Step 1: Run Offline Indexing (One-Time Setup)
Indexes all `.py` files in `Naive_RAG/` into Pinecone:
```powershell
python code_helper/index_codebase.py
```

### 4. Step 2: Run the Helper
Choose any of the three run interfaces:

#### Option A: Terminal Interactive Mode
```powershell
adk run code_helper
```

#### Option B: Official ADK Web Dashboard
```powershell
adk web
```
*(Open `http://localhost:8000` to interact with the visual agent graph).*

#### Option C: Custom Observatory Web App
```powershell
python frontend/server.py
```
*(Open `http://localhost:8080` for the real-time agent visualizer and metrics panel).*

### 5. Step 3: Run the Test & Evaluation Benchmark
```powershell
# Run the automated 5-question golden benchmark
python tests/test_golden_questions.py

# Run the comprehensive unit test suite
python -m pytest tests/
```

---

## 📊 Golden Evaluation Showcase

Recorded directly from automated execution of `tests/test_golden_questions.py` (persisted in `tests/benchmark_results.json`):

<details open>
<summary><b>1. Code Search: "Where is the document chunking logic implemented?"</b></summary>

* **Routed Worker**: `code_searcher`
* **Tools Invoked**: `transfer_to_agent`, `rag_search`
* **Execution Time**: ~45.0s
* **Evaluation Match**: ✅ Passed (Pinpointed exact file and line ranges)
* **Model Response**:
```text
File: Naive_RAG/indexer.py
Lines: 240-264
Code:
    # 1. Ingestion
    raw_document = load_document(file_path=file_path)

    # 2. Chunking
    chunk_list = chunk_document(
        text=raw_document,
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
    )

    # 3. Embedding
    embedded_chunks = embed_chunks(
        chunks=chunk_list,
        config=config,
    )
```
</details>

<details open>
<summary><b>2. Architecture Mapping: "Which files import config.py?"</b></summary>

* **Routed Worker**: `architecture_mapper`
* **Tools Invoked**: `transfer_to_agent`, `find_import_dependencies`
* **Execution Time**: ~4.5s
* **Evaluation Match**: ✅ Passed (Exact AST analysis without AI guessing)
* **Model Response**:
```text
Files that import 'config':
- indexer.py (Line 26)
- main.py (Line 31)
- query_pipeline.py (Line 23)
- vector_store.py (Line 22)

[DEPENDENCY SEARCH COMPLETE]: Report these matching files directly to the user.
```
</details>

<details open>
<summary><b>3. Onboarding Guide: "I am new to this project. Where do I start?"</b></summary>

* **Routed Worker**: `onboarding_guide`
* **Tools Invoked**: `transfer_to_agent`, `get_project_quickstart_and_modules`
* **Execution Time**: ~23.8s
* **Evaluation Match**: ✅ Passed (Authoritative orientation & reading order)
* **Model Response**:
```text
Naive_RAG Project Onboarding Guide:
1. Purpose: A reference 8-stage RAG system using NVIDIA NIM and Pinecone.
2. Recommended Reading Order:
   - config.py (Settings & credentials)
   - indexer.py (Offline indexing: Read -> Split -> Embed -> Store)
   - vector_store.py (Pinecone client and cosine similarity)
   - query_pipeline.py (Online query: Embed -> Retrieve -> Augment -> Generate)
   - main.py (Interactive CLI demonstration)
3. Run Commands:
   - Full Demo: python main.py
   - Indexing Only: python main.py --index
   - Custom Query: python main.py --query '<question>'
   - Compare: python main.py --compare
```
</details>

<details>
<summary><b>4. Code Explainer: "Explain vector_store.py in detail."</b></summary>

* **Routed Worker**: `code_explainer`
* **Tools Invoked**: `transfer_to_agent`, `read_file` *(Filesystem MCP)*
* **Execution Time**: ~23.1s
* **Evaluation Match**: ✅ Passed (Complete architectural breakdown via MCP)
* **Model Response**:
```text
The vector_store.py file is a Python module that provides an interface to manage vector databases using Pinecone Serverless. It includes functions for initializing, upserting, and querying vector embeddings, with a local fallback to a transparent JSON vector store.

Core functions:
- calculate_cosine_similarity: Calculates cosine similarity between two vectors using basic math (dot products and Euclidean norms).
- get_pinecone_client: Instantiates and returns the modern Pinecone client.
- ensure_pinecone_index_exists: Validates that the Pinecone Serverless index exists, creating it if necessary.
- upsert_to_vector_db: Batches and stores chunk embeddings and metadata into Pinecone or local fallback.
- query_vector_db: Retrieves top-k most similar chunks for a query vector.
```
</details>

<details>
<summary><b>5. Negative Grounding: "Where is Stripe payment billing handled?"</b></summary>

* **Routed Worker**: `code_searcher`
* **Tools Invoked**: `transfer_to_agent`, `rag_search`
* **Execution Time**: ~7.5s
* **Evaluation Match**: ✅ Passed (Refused to hallucinate non-existent features)
* **Model Response**:
```text
I could not find that in the codebase.
```
</details>

---

## 🛡️ Engineering Challenges & Production Fixes

### 1. Windows UTF-8 Terminal Encoding (`UnicodeDecodeError`)
* **Problem**: Running on Windows with the default `cp1252` encoding triggered `UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d...` when streaming LLM responses or printing file paths containing UTF-8 characters.
* **Fix**: Configured `PYTHONUTF8=1` in `.env` and introduced defensive stream reconfiguration in all CLI runners:
  ```python
  if sys.stdout and hasattr(sys.stdout, "reconfigure"):
      sys.stdout.reconfigure(encoding="utf-8", errors="replace")
  ```

### 2. LiteLLM Environment Variable Key Synchronization
* **Problem**: LiteLLM specifically resolves NVIDIA NIM authentication under `NVIDIA_NIM_API_KEY`, whereas the NVIDIA developer portal standard uses `NVIDIA_API_KEY`. Missing either variable caused authentication crashes in `google-adk`.
* **Fix**: Implemented a bidirectional key synchronizer in `code_helper/config.py` and `code_helper/__init__.py` that automatically detects, validates, and mirrors keys between `NVIDIA_API_KEY` and `NVIDIA_NIM_API_KEY`.

### 3. Agent Tool-Calling Infinite Loops
* **Problem**: Worker agents would occasionally call their assigned tools multiple times consecutively instead of synthesizing a final textual response after receiving tool output.
* **Fix**:
  1. Set strict prompt constraints: `"Call tool EXACTLY ONCE. As soon as the tool returns, formulate your final answer immediately."`
  2. Applied agent isolation: `disallow_transfer_to_parent=True` and `disallow_transfer_to_peers=True` on all workers.
  3. Added an automated execution safety guard in benchmark runners that halts loops once the target tool has returned data.

### 4. Hallucination on Out-of-Scope Code Questions
* **Problem**: When asked about features not in the codebase (e.g., Stripe billing), Pinecone still returns the mathematical nearest neighbors. Without a grounding guard, the model attempted to connect unrelated code to the query.
* **Fix**: Added a keyword grounding check and similarity threshold (`0.72`) in `rag_search`. If query keywords are missing from retrieved chunks and the similarity score is below the threshold, the tool explicitly returns `"No relevant code passages found in the codebase."`, and the worker answers `"I could not find that in the codebase."`

---

## ✅ Student Guide Compliance Checklist

| Guide Requirement | Implementation Detail | Status |
| :--- | :--- | :---: |
| **1 Boss that only routes** | `coordinator` agent uses `transfer_to_agent` and never answers code questions directly | ✅ **Verified** |
| **4 Workers with clear descriptions** | `code_searcher`, `code_explainer`, `architecture_mapper`, `onboarding_guide` | ✅ **Verified** |
| **5 or more tools, 1 with no AI** | 6 custom tools implemented; 4 tools run plain deterministic Python (`ast`, `pathlib`) | ✅ **Verified** |
| **Your own RAG, all 5 steps** | Manual 5-stage pipeline: Read, Split, Embed, Store, Search (No LangChain/LlamaIndex) | ✅ **Verified** |
| **Filesystem MCP on Code Explainer** | `@modelcontextprotocol/server-filesystem` via `npx` with `read_file` & `list_directory` | ✅ **Verified** |
| **Chunking explained in README** | Detailed comparison table and technical rationale for 500-char / 100-overlap chunks | ✅ **Verified** |
| **Keys in .env, not in the code** | Isolated in `.env`, guarded by `.gitignore`, with template provided in `.env.example` | ✅ **Verified** |
| **Runs with `adk run` or `adk web`** | Verified on ADK CLI terminal runner, ADK web interface, and custom web observatory | ✅ **Verified** |
| **3 sample questions & problem fix** | 5 benchmarked evaluations with recorded outputs and 4 documented problem fixes | ✅ **Verified** |

---

<div align="center">
  <sub>Built with ❤️ using Google ADK, NVIDIA NIM, and Pinecone Serverless.</sub>
</div>