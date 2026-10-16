"""
code_helper/tools/search_tools.py — Custom RAG Search Tool for Code Searcher Agent.

Provides semantic similarity search across the target codebase via NVIDIA NIM
embeddings and Pinecone Serverless.
"""
from openai import OpenAI
from pinecone import Pinecone
from code_helper.config import config


def rag_search(query: str, top_k: int = 3) -> str:
    """
    Search the codebase semantically for functions, classes, variables, or logic.
    
    Use this tool whenever the user asks where something is located in the code,
    which file implements a feature, or where a specific operation happens.
    
    Args:
        query: The semantic search query describing the code to find.
        top_k: Number of most relevant code chunks to retrieve (default: 3).
        
    Returns:
        A formatted string containing the top code snippets, their source file names,
        and line numbers. If nothing relevant is found, returns an empty notice.
    """
    cleaned_query = str(query).strip()
    if not cleaned_query:
        return "Error: Search query cannot be empty."

    # Defensive type casting: LLMs frequently pass integer arguments as strings (e.g. "3")
    try:
        top_k_int = int(top_k)
    except (ValueError, TypeError):
        top_k_int = 3

    try:
        # 1. Embed query with NVIDIA NIM
        client = OpenAI(
            base_url=config.nvidia_base_url,
            api_key=config.nvidia_api_key,
        )
        response = client.embeddings.create(
            input=[cleaned_query],
            model=config.embed_model,
        )
        query_vector = response.data[0].embedding

        # 2. Query Pinecone Serverless
        pc = Pinecone(api_key=config.pinecone_api_key)
        index = pc.Index(config.pinecone_index_name)

        search_result = index.query(
            vector=query_vector,
            top_k=top_k_int,
            include_metadata=True,
        )

        matches = search_result.matches
        if not matches:
            return "No relevant code passages found in the codebase."

        # Check if non-trivial query keywords appear in the retrieved chunks
        stop_words = {"where", "what", "which", "when", "how", "implemented", "handled", "code", "codebase", "does", "this", "that", "logic", "find", "search", "show"}
        cleaned_words = [w.strip("?,.!\"'();:").lower() for w in cleaned_query.split()]
        key_tokens = [w for w in cleaned_words if len(w) > 3 and w not in stop_words]

        has_token_match = False
        for m in matches:
            chunk_txt = (m.metadata or {}).get("text", "").lower()
            if any(token in chunk_txt for token in key_tokens):
                has_token_match = True
                break

        # If specific keywords were queried but none exist in the codebase and score is baseline
        if key_tokens and not has_token_match and float(matches[0].score) < 0.72:
            return "No relevant code passages found in the codebase."

        # 3. Format results with provenance
        formatted_blocks = []
        for rank, match in enumerate(matches, 1):
            meta = match.metadata or {}
            score = float(match.score)
            file_name = meta.get("file_name", "unknown")
            file_path = meta.get("file_path", file_name)
            start_line = meta.get("start_line", 0)
            end_line = meta.get("end_line", 0)
            text = meta.get("text", "")

            block = (
                f"--- Result {rank} (Relevance: {score:.3f}) ---\n"
                f"File: {file_path}\n"
                f"Lines: {start_line}-{end_line}\n"
                f"Code:\n{text}\n"
            )
            formatted_blocks.append(block)

        return "\n".join(formatted_blocks)

    except Exception as err:
        return f"Error executing RAG search: {str(err)}"
