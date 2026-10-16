# 🎓 Beginner's Complete Master Guide: Multi-Agent Code Helper
### *Everything you need to know about how this project was designed, built, and executed from absolute scratch.*

---

## 📌 Table of Contents
1. [What is this Project? (The Big Picture)](#1-what-is-this-project-the-big-picture)
2. [Vocabulary: Words You Need to Know (From the PDF)](#2-vocabulary-words-you-need-to-know-from-the-pdf)
3. [The Code Project We Are Studying (`Naive_RAG`)](#3-the-code-project-we-are-studying-naiverag)
4. [The 5 AI Agents: 1 Boss and 4 Workers](#4-the-5-ai-agents-1-boss-and-4-workers)
5. [How We Used Google ADK (Agent Development Kit)](#5-how-we-used-google-adk-agent-development-kit)
6. [How We Used MCP (Model Context Protocol)](#6-how-we-used-mcp-model-context-protocol)
7. [Which RAG We Built and WHY (All 5 Steps Explained)](#7-which-rag-we-built-and-why-all-5-steps-explained)
8. [Chunking Strategy: Why 500 Chunks with 100 Overlap?](#8-chunking-strategy-why-500-chunks-with-100-overlap)
9. [The Tools We Built (Plain Python vs AI Tools)](#9-the-tools-we-built-plain-python-vs-ai-tools)
10. [Answers to All Benchmark Questions (From Real Runs)](#10-answers-to-all-benchmark-questions-from-real-runs)
11. [Problems We Hit and How We Fixed Them](#11-problems-we-hit-and-how-we-fixed-them)
12. [Exact Commands to Run the Project](#12-exact-commands-to-run-the-project)

---

## 1. What is this Project? (The Big Picture)

Imagine you just joined a software company. On your first day, your boss hands you a folder containing a Python project you have never seen before. 

Naturally, you have four big questions:
1. **"Where is the code that does X?"** *(e.g., Where is the file chunking done?)*
2. **"What does this entire file do?"** *(e.g., Explain vector_store.py to me)*
3. **"How are the files connected together?"** *(e.g., Which files import config.py?)*
4. **"I am new here! Where do I even start?"** *(e.g., What does the project do, and how do I run it?)*

Usually, you would have to spend days reading every line of code to figure this out. 

**This project builds an automated team of 5 AI agents to do this for you:**
- **1 Boss (Coordinator)**: Listens to your question, decides which specialist is best suited for the job, and transfers the question to that specialist. **The Boss never tries to answer technical questions itself.**
- **4 Specialist Workers**:
  1. **Code Searcher**: Uses AI vector search (RAG) to pinpoint exact lines of code.
  2. **Code Explainer**: Uses an industry-standard file reader (MCP) to read a whole file and explain it.
  3. **Architecture Mapper**: Uses plain, 100% deterministic Python syntax inspection (AST) to see which files import which other files—**with zero AI guessing**.
  4. **Onboarding Guide**: Tells newcomers what the project does, in what order to read the files, and which commands to execute.

---

## 2. Vocabulary: Words You Need to Know (From the PDF)

If you are new to AI agents, RAG, and vector databases, here is a simple explanation of every key term from Page 2 of the student guide:

| Word | What it Means (In Plain English) | Real-World Analogy |
| :--- | :--- | :--- |
| **Agent** | An AI program that can read a prompt, reason about what needs to be done, choose tools to gather information, and reply. | A smart assistant with a toolbox. |
| **Boss (Coordinator)** | The manager agent. Its only job is to pick the right worker. It never answers technical questions itself. | A hospital triage receptionist who directs patients to the doctor, surgeon, or pharmacist. |
| **Worker** | A sub-agent with one specific job and its own dedicated set of tools. | A specialist doctor (e.g., cardiologist). |
| **Tool** | A normal Python function that an agent can decide to call when it needs information. | A calculator or microscope the specialist uses. |
| **RAG** *(Retrieval-Augmented Generation)* | A technique where you cut a big pile of documents into small pieces, store them, find the pieces closest to the user's question, and hand them to the AI to answer from. | An **open-book exam**. Instead of memorizing the whole textbook, the student flips open the book to the exact page needed to answer the question. |
| **Chunk** | A small slice of text or code (e.g., 500 characters). | One paragraph on a page. |
| **Embedding** | Converting words or code into a list of numbers (coordinates) that represents its *meaning*. | Giving a concept a GPS coordinate in a map of ideas. "Dog" and "Puppy" are close together; "Dog" and "Airplane" are far apart. |
| **Vector Database (Pinecone)** | A cloud database built specifically to find which lists of numbers (embeddings) are closest to each other. | A super-fast GPS search engine for text meanings. |
| **MCP Server** *(Model Context Protocol)* | A standardized background program that gives an AI agent ready-made tools (like reading files on your computer) without you having to code them from scratch. | A **USB-C cable** that connects any accessory (microphone, mouse) to your laptop using a standard plug. |
| **AST** *(Abstract Syntax Tree)* | Python's built-in way of reading code like grammatical rules (finding every `import`, `class`, or `def` line with 100% mathematical certainty). | An X-ray machine for Python code. |

---

## 3. The Code Project We Are Studying (`Naive_RAG`)

Our Multi-Agent Code Helper is designed to analyze a specific target codebase located in the folder `Naive_RAG/`. 

This target codebase is a small 5-file Python project:
1. **`config.py`**: Holds settings, model names, API keys, and chunking hyperparameters.
2. **`indexer.py`**: The offline pipeline that loads documents, cuts them into chunks, embeds them, and uploads them.
3. **`vector_store.py`**: Interacts with the Pinecone vector database (creates indexes, upserts vectors, queries cosine similarity).
4. **`query_pipeline.py`**: The online pipeline that takes a user query, embeds it, retrieves the top chunks, and generates an answer.
5. **`main.py`**: The CLI menu that ties everything together.

---

## 4. The 5 AI Agents: 1 Boss and 4 Workers

```
                     ┌────────────────────────┐
                     │    BOSS (Coordinator)  │
                     │  "Never answer yourself│
                     │  Pick the best worker" │
                     └───────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼                       ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  Code Searcher   │   │  Code Explainer  │   │Architecture Mapper│  │ Onboarding Guide │
│ "Where is code?" │   │ "Explain a file" │   │ "How files link" │   │ "Where to start" │
│                  │   │                  │   │                  │   │                  │
│ Tool: rag_search │   │ Tool: read_file  │   │ Tools: AST tools │   │ Tool: Quickstart │
│  (Pinecone RAG)  │   │ (Filesystem MCP) │   │ (No AI guessing) │   │ (Curated Guide)  │
└──────────────────┘   └──────────────────┘   └──────────────────┘   └──────────────────┘
```

### 1. The Boss (`coordinator`)
* **Job**: Receives any question from the user. Decides which worker is the right one and immediately executes `transfer_to_agent`.
* **Golden Rule**: **NEVER answers technical questions directly.**

### 2. Worker 1: `code_searcher`
* **Job**: Finds where functions, classes, or features are implemented.
* **Tool**: `rag_search` (Custom 5-step RAG using Pinecone and NVIDIA embeddings).
* **Example Question**: *"Where is the document chunking logic implemented?"*

### 3. Worker 2: `code_explainer`
* **Job**: Reads entire files from start to finish and explains their design, functions, and classes.
* **Tool**: `read_file` and `list_directory` provided by the **Filesystem MCP Server**.
* **Example Question**: *"Explain vector_store.py in detail."*

### 4. Worker 3: `architecture_mapper`
* **Job**: Analyzes imports, module dependencies, function lists, and repository folder trees.
* **Tools**: `find_import_dependencies`, `get_file_outline`, `get_codebase_tree`.
* **Important**: Uses **Plain Python (`ast` and `pathlib`)** — **No AI guessing!**
* **Example Question**: *"Which files import config.py?"*

### 5. Worker 4: `onboarding_guide`
* **Job**: Orients new developers on the project's purpose, recommended reading order, and CLI run commands.
* **Tool**: `get_project_quickstart_and_modules`.
* **Example Question**: *"I am new to this project. Where do I start?"*

---

## 5. How We Used Google ADK (Agent Development Kit)

### What is Google ADK?
Google ADK (`google-adk`) is Google's modern framework for creating AI agents. It gives you ready-to-use classes:
- **`LlmAgent`**: Represents an agent with a name, a model, instructions, and tools.
- **`LiteLlm`**: A model wrapper that lets ADK talk to any LLM (in our case, NVIDIA NIM's `meta/llama-3.2-11b-vision-instruct`).
- **`sub_agents`**: A list of workers assigned to a boss agent.
- **`transfer_to_agent`**: Built-in routing mechanism that the boss calls to pass control to a worker.

### How We Implemented It in `code_helper/agent.py`

#### 1. Setting up the shared LLM model
```python
from google.adk.models.lite_llm import LiteLlm

# One shared model object used by all 5 agents
model = LiteLlm(
    model="nvidia_nim/meta/llama-3.2-11b-vision-instruct",
    api_key=config.nvidia_api_key,
)
```

#### 2. Building a Worker (`code_searcher`)
```python
from google.adk.agents import LlmAgent
from code_helper.tools.search_tools import rag_search

searcher = LlmAgent(
    name="code_searcher",
    model=model,
    description="Finds where specific features or logic are implemented in the code using RAG search.",
    instruction="Call rag_search EXACTLY ONCE with the search query. Deliver your final answer directly to the user.",
    tools=[rag_search],
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)
```

#### 3. Building the Boss (`coordinator`)
```python
root_agent = LlmAgent(
    name="coordinator",
    model=model,
    description="Sends each question to the right worker.",
    instruction=(
        "You are the coordinator boss. You NEVER answer technical or codebase questions yourself.\n"
        "You MUST immediately transfer to exactly one worker agent using transfer_to_agent:\n"
        "- Where something is located -> transfer to 'code_searcher'\n"
        "- Explain a file in detail -> transfer to 'code_explainer'\n"
        "- Imports, dependencies, or outlines -> transfer to 'architecture_mapper'\n"
        "- Where to start / onboarding overview -> transfer to 'onboarding_guide'\n"
    ),
    sub_agents=[searcher, explainer, mapper, guide],
)
```

---

## 6. How We Used MCP (Model Context Protocol)

### What is MCP and Why Use It?
The student guide explicitly states in Section 6 & 8:
> *"The Code Explainer reads whole files through the Filesystem MCP server. You do not write a function for it. You connect it and its tools appear on the agent."*

Instead of coding custom file-reading Python functions, **MCP is an open standard created by Anthropic** that lets an agent connect to existing tool servers. 

We used the official Node.js package: `@modelcontextprotocol/server-filesystem`.

### How We Wired MCP into ADK:
```python
import shutil
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

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

# Hand the MCP toolset directly to the code_explainer agent!
explainer = LlmAgent(
    name="code_explainer",
    model=model,
    description="Reads a whole file and explains its architecture using filesystem MCP.",
    tools=[file_tools],
)
```

### Why MCP for Code Explainer vs RAG for Code Searcher?
- **RAG** cuts code into small pieces (chunks). This is great when asking: *"Where is line X?"*
- But when you ask: *"Explain vector_store.py"*, RAG would only return small disjointed snippets. **The Code Explainer needs the entire file unbroken.** The Filesystem MCP server allows it to read the complete file directly from disk safely!

---

## 7. Which RAG We Built and WHY (All 5 Steps Explained)

The student guide states in Section 6:
> *"Build each step yourself. Do not use LlamaIndex or LangChain for this."*

We built our own custom 5-step RAG pipeline from scratch in `code_helper/index_codebase.py` and `code_helper/tools/search_tools.py`:

```
1. READ ───────► 2. SPLIT ───────► 3. EMBED ───────► 4. STORE ───────► 5. SEARCH
(Load .py files) (Cut chunks)   (NVIDIA NIM)      (Pinecone)       (Cosine Query)
```

### The 5 Steps:
1. **Step 1: Read (`read_codebase`)**:
   Reads all 5 Python files in `Naive_RAG/` using Python's `open()` with `utf-8` encoding. It records the file name, line count, and character count.
2. **Step 2: Split (`split_into_chunks`)**:
   Slices the text into chunks of **500 characters** with **100 characters of overlap**. It calculates the exact `start_line` and `end_line` for every chunk so we can report line numbers later.
3. **Step 3: Embed (`embed_chunks`)**:
   Takes each chunk and sends it to the **NVIDIA NIM API** (`nvidia/nemotron-3-embed-1b`). NVIDIA turns the chunk text into a list of **2048 decimal numbers** (the embedding vector).
4. **Step 4: Store (`store_in_pinecone`)**:
   Connects to **Pinecone Serverless** (`code-helper` index) on AWS `us-east-1` with `metric="cosine"`. Uploads each vector along with metadata (`file_name`, `start_line`, `end_line`, and `text`).
5. **Step 5: Search (`rag_search`)**:
   When the user asks *"Where is chunking done?"*, this tool sends that query to NVIDIA NIM to get its 2048-dimensional vector, asks Pinecone for the 3 nearest vectors (highest cosine similarity), and formats the output with line numbers.

---

## 8. Chunking Strategy: Why 500 Chunks with 100 Overlap?

In RAG, **chunk size** is the most critical tuning decision. There is no single universal number, but code has unique properties compared to normal English paragraphs:

| Chunk Size Choice | What Happens | Why It Is Good or Bad |
| :--- | :--- | :--- |
| **Small (200 characters)** | Functions get cut in half. | **Bad**: A function signature gets separated from its body. The AI cannot understand what the function does because it only sees half of it. |
| **Large (1500 characters)** | 3 or 4 different functions get mashed into one chunk. | **Bad**: When you search for one specific function, Pinecone retrieves a giant block containing unrelated code, confusing the AI and diluting vector precision. |
| **Selected (500 characters, 100 overlap)** | Exactly 1 function, class header, or docstring block. | **Optimal**: In `Naive_RAG`, functions like `load_document()` or `calculate_cosine_similarity()` are naturally 300–450 characters long. A 500-character chunk holds the whole function, and the 100-character overlap ensures lines on the boundary are never lost. |

---

## 9. The Tools We Built (Plain Python vs AI Tools)

The student guide states in Section 5:
- Build at least 5 tools.
- Every worker gets at least one tool.
- At least one tool uses no AI (plain Python).
- MCP tools do not count toward the 5.

Here are the 6 custom tools we wrote:

### 1. `rag_search` (AI / Vector Search)
* **Used by**: `code_searcher`
* **How it works**: Queries NVIDIA NIM embeddings and Pinecone. Returns exact file paths and line ranges.

### 2. `find_import_dependencies` (Plain Python - NO AI)
* **Used by**: `architecture_mapper`
* **How it works**: Uses Python's built-in `ast.parse()`. It traverses every file looking for `import config` or `from config import ...`. It returns exact file names and line numbers with 100% mathematical certainty. **No AI guessing involved!**

### 3. `get_file_outline` (Plain Python - NO AI)
* **Used by**: `architecture_mapper`
* **How it works**: Uses Python's `ast` module to extract all `class` and `def` function names along with their starting and ending lines.

### 4. `get_codebase_tree` (Plain Python - NO AI)
* **Used by**: `architecture_mapper`
* **How it works**: Uses Python's `pathlib` to scan the folder and return the list of Python files.

### 5. `get_project_quickstart_and_modules` (Plain Python - NO AI)
* **Used by**: `onboarding_guide`
* **How it works**: Returns a structured overview explaining what `Naive_RAG` does, which order to read the files in, and what commands to run.

### 6. `read_code_file` (Plain Python - NO AI)
* **Used by**: Standalone offline testing
* **How it works**: Reads a file safely with numbered lines.

---

## 10. Answers to All Benchmark Questions (From Real Runs)

During testing, we executed the 5 canonical golden evaluation questions through the Boss coordinator (`tests/test_golden_questions.py`). Here are the real results:

### Question 1: Code Search
> **User Prompt**: *"Where is the document chunking logic implemented?"*
* **Which Agent Answered**: `code_searcher`
* **Tool Used**: `rag_search`
* **Actual Answer Produced**:
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
```

### Question 2: Architecture Mapping
> **User Prompt**: *"Which files import config.py?"*
* **Which Agent Answered**: `architecture_mapper`
* **Tool Used**: `find_import_dependencies`
* **Actual Answer Produced**:
```text
Files that import 'config':
- indexer.py (Line 26)
- main.py (Line 31)
- query_pipeline.py (Line 23)
- vector_store.py (Line 22)
```

### Question 3: Onboarding Guide
> **User Prompt**: *"I am new to this project. Where do I start?"*
* **Which Agent Answered**: `onboarding_guide`
* **Tool Used**: `get_project_quickstart_and_modules`
* **Actual Answer Produced**:
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

### Question 4: Code Explanation
> **User Prompt**: *"Explain vector_store.py in detail."*
* **Which Agent Answered**: `code_explainer`
* **Tool Used**: `read_file` (via Filesystem MCP Server)
* **Actual Answer Produced**:
```text
vector_store.py provides an interface to manage vector databases using Pinecone Serverless. It includes functions for initializing, upserting, and querying vector embeddings, with a local fallback to a JSON vector store.

Key components:
- calculate_cosine_similarity: Computes cosine similarity between vectors using dot products and norms.
- get_pinecone_client: Instantiates the Pinecone client.
- ensure_pinecone_index_exists: Validates that the Serverless index is present or creates it.
- upsert_to_vector_db: Batches and uploads vector embeddings and metadata.
- query_vector_db: Queries top-k most similar chunks for query vectors.
```

### Question 5: Negative Grounding / Hallucination Test
> **User Prompt**: *"Where is Stripe payment billing handled?"*
* **Which Agent Answered**: `code_searcher`
* **Tool Used**: `rag_search`
* **Actual Answer Produced**:
```text
I could not find that in the codebase.
```
*(As required by Page 5 of the PDF: "Tell your agents to say 'I could not find that' when the search finds nothing. An agent that admits it does not know is better than one that makes something up.")*

---

## 11. Problems We Hit and How We Fixed Them

### 1. Windows Unicode Error (`UnicodeDecodeError`)
* **Problem**: Windows terminal defaults to `cp1252` encoding. Whenever an agent printed special characters, Python crashed with a `UnicodeDecodeError`.
* **Fix**: Added `PYTHONUTF8=1` in `.env` and added `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` in our Python scripts.

### 2. LiteLLM Key Variable Name Mismatch
* **Problem**: LiteLLM looks for `NVIDIA_NIM_API_KEY`, but the NVIDIA website gave us a key labeled `NVIDIA_API_KEY`. If either was missing, the agents crashed.
* **Fix**: Wrote an automatic key synchronization check in `code_helper/config.py` that mirrors `NVIDIA_API_KEY` to `NVIDIA_NIM_API_KEY`.

### 3. Agent Looping (Calling Tools Repeatedly)
* **Problem**: When a worker received data from its tool, it sometimes called the same tool again in an infinite loop instead of giving the answer to the user.
* **Fix**:
  - Added strict prompt instructions: `"Call tool EXACTLY ONCE. Formulate your final answer immediately."`
  - Set `disallow_transfer_to_parent=True` and `disallow_transfer_to_peers=True` on all workers.
  - Added a timeout and safety circuit breaker in tests.

### 4. Hallucinating Answers on Missing Code
* **Problem**: When asked about "Stripe billing" (which is NOT in `Naive_RAG`), Pinecone still returned the 3 mathematically closest chunks. Without a safeguard, the LLM attempted to pretend those chunks handled billing.
* **Fix**: Added a keyword grounding check and similarity threshold (`0.72`) in `rag_search`. If query keywords are missing and score is low, the tool returns `"No relevant code passages found"`, and the agent truthfully answers `"I could not find that in the codebase."`

---

## 12. Exact Commands to Run the Project

### Step 1: Open PowerShell in the project directory
```powershell
cd "E:\DEBO ASSIGNMENT 2"
```

### Step 2: Create and activate virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install all dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Verify your `.env` file exists
Make sure your `.env` file contains your valid keys:
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

### Step 5: Run the 5-Step RAG Indexer (Run Once)
This reads `Naive_RAG/*.py`, creates 500-char chunks, embeds them with NVIDIA NIM, and stores them in Pinecone:
```powershell
python code_helper/index_codebase.py
```

### Step 6: Chat with the Agents!
**In Terminal:**
```powershell
adk run code_helper
```
*(Type your questions like "Which files import config.py?" or "Where is chunking done?" and see the Boss route to the right worker!)*

**In Web Browser:**
```powershell
adk web
```
*(Open http://localhost:8000 to see the visual agent graph).*

**Run the Automated Benchmark Suite:**
```powershell
python tests/test_golden_questions.py
```
*(Runs all 5 golden questions and outputs `tests/benchmark_results.json`).*

---

<div align="center">
  <b>Project Repository:</b> <a href="https://github.com/tanishka-jadhav/CODE-HELPER-">github.com/tanishka-jadhav/CODE-HELPER-</a>
</div>
