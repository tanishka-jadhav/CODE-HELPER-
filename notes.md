# 🎤 Presentation & Viva Defense Notes
## Project: Multi-Agent Code Helper
### *A Complete Step-by-Step Guide on How to Explain This Project to Sir From Scratch*

---

## 📌 How to Use These Notes
These notes are written as a **spoken presentation script**. You can use them to walk your professor, mentor, or evaluator ("Sir") through your project from the high-level motivation down to the deepest lines of code.

---

## 🕒 Quick 2-Minute Elevator Pitch (Memorize This!)

> *"Good morning/afternoon, Sir.*
> 
> *Today I am presenting the **Multi-Agent Code Helper**.*
> 
> *When an engineer joins a new software project, the biggest bottleneck is understanding unfamiliar code: 'Where is this feature implemented?', 'What does this file do?', 'Which files import this module?', and 'Where do I even start?'*
> 
> *Standard AI models often hallucinate or guess when asked technical questions about code. To solve this, I designed and built an **autonomous multi-agent system** using **Google's Agent Development Kit (ADK)**, **NVIDIA NIM** for embeddings and chat, and **Pinecone Serverless** for vector search.*
> 
> *The system follows a strict **Coordinator-Worker pattern**:*
> * *We have **1 Boss (Coordinator)** whose sole job is intent recognition and routing. The Boss **never** answers technical questions directly.*
> * *We have **4 specialized Worker agents**:*
>   1. ***Code Searcher***, *which uses our custom 5-step RAG pipeline to pinpoint code and line numbers.*
>   2. ***Code Explainer***, *which connects to a Model Context Protocol (MCP) Filesystem server to read whole files safely.*
>   3. ***Architecture Mapper***, *which uses deterministic Python AST syntax trees to map imports with 100% mathematical accuracy—no AI guessing.*
>   4. ***Onboarding Guide***, *which provides orientation, reading orders, and CLI commands.*
> 
> *All 5 benchmark tests passed with 100% grounding, and the system is fully operational across the terminal, the ADK Web UI, and our custom real-time simulator dashboard."*

---

## 📑 Slide-by-Slide Detailed Presentation Script

---

### Part 1: Problem Statement & Motivation
**What you should say:**
> *"Sir, single LLMs struggle with large code repositories for three reasons:*
> 1. *Their context window cannot hold entire enterprise projects without getting slow and expensive.*
> 2. *They hallucinate dependencies and make up function names that do not exist.*
> 3. *Different questions require different tools: searching for a snippet requires semantic vector search, but mapping imports requires exact syntax tree analysis, and explaining an entire file requires reading the whole unchunked source code.*
> 
> *Therefore, one single prompt or agent is insufficient. We need a **team of specialized agents**, each with dedicated tools and boundaries."*

---

### Part 2: The Target Codebase (`Naive_RAG`)
**What you should say:**
> *"Sir, the codebase our helper analyzes is a reference 5-file Python project called `Naive_RAG/`:*
> * `config.py`: *Holds environment variables, model configurations, and hyperparameters.*
> * `indexer.py`: *The offline pipeline that reads documents, chunks them, embeds them, and uploads to vector DB.*
> * `vector_store.py`: *Pinecone client integration, cosine similarity calculation, and JSON fallback.*
> * `query_pipeline.py`: *Online query pipeline that embeds questions, searches Pinecone, and synthesizes answers.*
> * `main.py`: *Interactive CLI demonstration tool.*
> 
> *Our helper inspects and explains these 5 files with zero human intervention."*

---

### Part 3: System Architecture (The 5 Agents)
**What you should say:**
> *"Sir, the architecture consists of 1 Coordinator Boss and 4 Specialist Workers built with Google ADK:*
> 
> 1. **The Boss (`coordinator`)**:
>    * *Rule: It NEVER answers code questions itself.*
>    * *It evaluates the user's intent and calls ADK's built-in `transfer_to_agent` function to delegate execution to the right worker.*
> 
> 2. **Worker 1: `code_searcher`**:
>    * *Job: Answers 'Where is feature X implemented?'.*
>    * *Tool: `rag_search`.*
>    * *It queries our Pinecone vector database and returns exact files and line ranges (e.g., `indexer.py lines 240-264`).*
> 
> 3. **Worker 2: `code_explainer`**:
>    * *Job: Answers 'Explain vector_store.py in detail'.*
>    * *Tool: Built-in `read_file` from the **Filesystem MCP Server**.*
>    * *Why MCP? Because RAG cuts files into small chunks. But to explain a whole file, the agent needs the full, unchunked code. MCP gives it safe, sandboxed disk access.*
> 
> 4. **Worker 3: `architecture_mapper`**:
>    * *Job: Answers 'Which files import config.py?'.*
>    * *Tools: `find_import_dependencies`, `get_file_outline`, `get_codebase_tree`.*
>    * *Key Feature: **Zero AI Guessing.** It uses Python's standard library `ast` (Abstract Syntax Tree) module to parse code grammar with 100% mathematical precision.*
> 
> 5. **Worker 4: `onboarding_guide`**:
>    * *Job: Answers 'I am new. Where do I start?'.*
>    * *Tool: `get_project_quickstart_and_modules`.*
>    * *It gives new developers an orientation roadmap: what the project does, the recommended reading order, and CLI commands."*

---

### Part 4: The 5-Step Custom RAG Pipeline (Built from Scratch)
**What you should say:**
> *"Sir, per Section 6 of the Student Guide, we were strictly instructed **NOT** to use LangChain or LlamaIndex. We built all 5 steps of the RAG pipeline manually in `code_helper/index_codebase.py` and `code_helper/tools/search_tools.py`:*
> 
> 1. **Step 1: Read (`read_codebase`)**:
>    * *Ingests all `.py` files in `Naive_RAG/` with UTF-8 encoding, computing line and character counts.*
> 
> 2. **Step 2: Split (`split_into_chunks`)**:
>    * *Slices code using a character sliding window.*
>    * *We chose **500 characters** with a **100-character overlap**.*
>    * *Crucially, we precompute newline offsets so every chunk knows its exact starting and ending line number in the original file.*
> 
> 3. **Step 3: Embed (`embed_chunks`)**:
>    * *Batches chunk text and sends it to NVIDIA NIM's `nvidia/nemotron-3-embed-1b` model.*
>    * *Generates high-dimensional dense vectors of **2048 dimensions**.*
> 
> 4. **Step 4: Store (`store_in_pinecone`)**:
>    * *Connects to Pinecone Serverless (index: `code-helper`, cloud: AWS `us-east-1`, metric: `cosine`).*
>    * *Upserts each vector with rich metadata: file name, file path, start line, end line, and the chunk code.*
> 
> 5. **Step 5: Search (`rag_search`)**:
>    * *When a query comes in, it embeds the question, queries Pinecone for the top 3 nearest vectors, applies our **grounding safety threshold (0.72)**, and formats the output with line citations."*

---

### Part 5: The Crucial "Why" Questions (Sir WILL Ask These!)

#### Question A: *"Why did you choose 500 characters chunk size with 100 overlap?"*
**Your Answer:**
> *"Sir, code is different from English prose. 
> * If we use **small chunks (200 chars)**: function headers get separated from their bodies, cutting docstrings in half. The vector loses semantic context.
> * If we use **large chunks (1500 chars)**: multiple unrelated functions get mashed into one chunk, which dilutes cosine similarity scores and injects noise.
> * **500 characters with 100 overlap** is the optimal sweet spot for Python modules. Most functions in `Naive_RAG` are 300 to 500 characters long, so one chunk captures the complete cohesive function while the 100-character overlap prevents boundary truncation."*

#### Question B: *"Why use MCP for the Code Explainer instead of RAG?"*
**Your Answer:**
> *"Sir, RAG is designed for pinpoint retrieval: finding 20 lines of code inside 5000 lines. 
> But when a developer asks to 'Explain vector_store.py', cutting that file into chunks and only retrieving the top 2 chunks would give an incomplete, broken explanation. 
> The Code Explainer needs the **entire unbroken file**. Model Context Protocol (MCP) allows us to safely connect an official filesystem tool (`@modelcontextprotocol/server-filesystem`) scoped strictly to `Naive_RAG/`, adhering to modern open standards."*

#### Question C: *"Why does the Architecture Mapper use plain Python AST instead of an LLM?"*
**Your Answer:**
> *"Sir, LLMs are probabilistic—they predict tokens based on likelihood. When asked 'Which files import config.py?', an LLM might guess or forget a file. 
> By using Python's built-in `ast` module, we inspect the literal Abstract Syntax Tree of the code. We scan every `Import` and `ImportFrom` node. The result is 100% mathematically exact, deterministic, and free of hallucination."*

#### Question D: *"How do you prevent the AI from hallucinating on features that don't exist (like Stripe)?"*
**Your Answer:**
> *"Sir, vector databases always return nearest neighbors, even if the similarity is very low. 
> To prevent hallucination, our `rag_search` tool implements a **two-layer grounding guard**:
> 1. It extracts non-trivial query keywords and verifies if at least one token actually appears in the retrieved chunks.
> 2. If no tokens match and the top cosine similarity score is below `0.72`, the tool explicitly returns 'No relevant code passages found'.
> 3. Following Page 5 of the Student Guide, the agent is instructed to truthfully answer: **'I could not find that in the codebase'** instead of fabricating an answer."*

---

## 💻 Live Demonstration Guide (What to Show on Screen)

During your presentation, open the browser at **`http://127.0.0.1:8080`** or the terminal via `adk run code_helper`. Run these 5 canonical questions in order:

```
┌─────────────────────────────────────────────────────────────┬───────────────────────┬───────────────────────────────┐
│ Question to Enter                                           │ Routed Worker         │ What to Point Out to Sir      │
├─────────────────────────────────────────────────────────────┼───────────────────────┼───────────────────────────────┤
│ 1. "Where is the document chunking logic implemented?"      │ code_searcher         │ Point to line numbers 240-264 │
│                                                             │                       │ in indexer.py from Pinecone.  │
├─────────────────────────────────────────────────────────────┼───────────────────────┼───────────────────────────────┤
│ 2. "Which files import config.py?"                          │ architecture_mapper   │ Show the 4 exact files found  │
│                                                             │                       │ via Python AST with no AI.    │
├─────────────────────────────────────────────────────────────┼───────────────────────┼───────────────────────────────┤
│ 3. "I am new to this project. Where do I start?"            │ onboarding_guide      │ Show the recommended reading  │
│                                                             │                       │ order and CLI run commands.   │
├─────────────────────────────────────────────────────────────┼───────────────────────┼───────────────────────────────┤
│ 4. "Explain vector_store.py in detail."                     │ code_explainer        │ Show how it uses Filesystem   │
│                                                             │                       │ MCP to explain the full file. │
├─────────────────────────────────────────────────────────────┼───────────────────────┼───────────────────────────────┤
│ 5. "Where is Stripe payment billing handled?"               │ code_searcher (refusal)│ Show that it admits "I could  │
│                                                             │                       │ not find that" (No guessing). │
└─────────────────────────────────────────────────────────────┴───────────────────────┴───────────────────────────────┘
```

---

## 🛠️ Real Engineering Challenges We Solved

Tell Sir about these real issues you debugged:

1. **Windows Terminal UTF-8 Encoding (`cp1252`)**:
   * *Problem*: Windows PowerShell crashed with `UnicodeDecodeError` when printing special characters.
   * *Solution*: Enforced `PYTHONUTF8=1` in `.env` and added `sys.stdout.reconfigure(encoding="utf-8")`.

2. **LiteLLM Key Variable Synchronization**:
   * *Problem*: Google ADK uses LiteLLM which expects `NVIDIA_NIM_API_KEY`, but NVIDIA provides `NVIDIA_API_KEY`.
   * *Solution*: Built a defensive key synchronization shim in `code_helper/config.py` that automatically mirrors keys.

3. **Preventing LLM Tool-Calling Infinite Loops**:
   * *Problem*: Agents in multi-agent frameworks sometimes repeatedly call tools without returning the final answer.
   * *Solution*: Enforced strict prompt instructions (`"Call tool EXACTLY ONCE"`), configured worker isolation (`disallow_transfer_to_parent=True`, `disallow_transfer_to_peers=True`), and added a safety circuit breaker.

---

## ❓ Top 10 Viva Questions & Bulletproof Answers

#### 1. What is Google ADK and why did you use it?
> *"Google ADK (Agent Development Kit) is Google's official Python framework for building composable, multi-agent workflows. It provides standard `LlmAgent` abstractions, native session management, tool binding, and hierarchical sub-agent routing via `transfer_to_agent`."*

#### 2. How does the Boss know which worker to pick?
> *"When we create the coordinator `LlmAgent`, we provide a clear `description` for each worker in `sub_agents=[searcher, explainer, mapper, guide]`. The LLM reads the user query, compares it against each worker's description, and invokes the built-in `transfer_to_agent` function with the chosen worker's name."*

#### 3. What is Model Context Protocol (MCP)?
> *"MCP is an open standard developed by Anthropic that allows AI applications to connect to external data sources and tools over JSON-RPC stdio. We used `@modelcontextprotocol/server-filesystem` executed through Node's `npx` to grant sandboxed read access to the target codebase."*

#### 4. What embedding model did you use, and what is its dimension?
> *"We used NVIDIA's `nvidia/nemotron-3-embed-1b`. It produces 2048-dimensional dense vector embeddings. The Pinecone index is explicitly configured for dimension 2048 and the cosine similarity metric."*

#### 5. What is the difference between Cosine Similarity and Euclidean Distance?
> *"Cosine similarity measures the angle between two vectors regardless of magnitude (scaled between -1 and 1), making it ideal for text and code semantic meaning. Euclidean distance measures straight-line distance, which can be distorted by document length."*

#### 6. Why did you not use LangChain or LlamaIndex?
> *"Section 6 of the Student Guide required us to build each step of RAG ourselves. Implementing reading, chunking, embedding, storage, and retrieval manually ensures we understand the exact mechanics, line provenance tracking, and error boundaries without black-box framework abstractions."*

#### 7. How are API keys secured in this project?
> *"Keys are strictly loaded from a `.env` file via `python-dotenv`. The `.env` file is explicitly ignored in `.gitignore`, and a `.env.example` template with placeholder values is provided for developers."*

#### 8. How did you verify the system works?
> *"We wrote an automated benchmark suite in `tests/test_golden_questions.py`. It executes all 5 canonical test questions through the Coordinator Boss using ADK's `InMemoryRunner`, verifying that 100% of the questions routed to the correct worker and returned verified line-cited answers."*

#### 9. Can this system be pointed at any other Python project?
> *"Yes, Sir. In `code_helper/config.py`, the `target_codebase_dir` can be pointed to any Python project folder. Running `python code_helper/index_codebase.py` once will index the new repository and the helper will immediately be ready to answer questions about it."*

#### 10. Where is this code hosted?
> *"The complete repository, along with tests, documentation, and web frontends, is version-controlled and hosted on GitHub at `https://github.com/tanishka-jadhav/CODE-HELPER-`."*

---

<div align="center">
  <b>Good luck with your presentation! You've got this! 🚀</b>
</div>
