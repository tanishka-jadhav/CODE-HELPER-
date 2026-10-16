"""
tests/test_retrieval.py — Step 5 (Search) Standalone Retrieval Verification.

Tests the query embedding and Pinecone vector search pipeline in isolation:
  1. Embeds user queries via NVIDIA NIM (2048-dim).
  2. Queries Pinecone Serverless index 'code-helper'.
  3. Formats results with file provenance (file_name, start_line, end_line, score).
  4. Tests relevance score filtering (detecting when to say 'I could not find that').
"""
import sys
import time
from pathlib import Path
from openai import OpenAI
from pinecone import Pinecone

# Ensure project root is in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code_helper.config import config


def search_codebase(query: str, top_k: int = 3, score_threshold: float = 0.50) -> list[dict]:
    """
    Step 5: Search
    Embeds the question and asks Pinecone for the closest code chunks.
    """
    print("\n" + "=" * 65)
    print(f"QUERY: \"{query}\"")
    print("=" * 65)

    # 1. Embed query with NVIDIA NIM
    client = OpenAI(
        base_url=config.nvidia_base_url,
        api_key=config.nvidia_api_key,
    )
    
    t0 = time.time()
    response = client.embeddings.create(
        input=[query],
        model=config.embed_model,
    )
    query_vector = response.data[0].embedding
    embed_ms = round((time.time() - t0) * 1000, 1)
    print(f"[*] Query embedded in {embed_ms}ms ({len(query_vector)} dims)")

    # 2. Query Pinecone Serverless
    pc = Pinecone(api_key=config.pinecone_api_key)
    index = pc.Index(config.pinecone_index_name)

    t1 = time.time()
    search_response = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
    )
    query_ms = round((time.time() - t1) * 1000, 1)
    print(f"[*] Pinecone search completed in {query_ms}ms")

    # 3. Parse and filter matches
    results = []
    print(f"\n[*] Top {top_k} Candidates Retrieved:")
    for rank, match in enumerate(search_response.matches, 1):
        meta = match.metadata or {}
        score = float(match.score)
        file_name = meta.get("file_name", "unknown")
        start_line = meta.get("start_line", 0)
        end_line = meta.get("end_line", 0)
        text = meta.get("text", "")

        is_relevant = score >= score_threshold
        status = "RELEVANT" if is_relevant else "BELOW THRESHOLD"

        print(f"  [Match #{rank}] Score: {score:.4f} [{status}]")
        print(f"    File: {file_name} (Lines {start_line}-{end_line})")
        preview = text.replace("\n", " ")[:90]
        print(f"    Code: \"{preview}...\"\n")

        if is_relevant:
            results.append({
                "rank": rank,
                "id": match.id,
                "score": score,
                "file_name": file_name,
                "start_line": start_line,
                "end_line": end_line,
                "text": text,
            })

    if not results:
        print(f"[RESULT] No chunks met score threshold ({score_threshold}).")
        print("         Agent must respond: \"I could not find that.\"")
    else:
        print(f"[RESULT] Found {len(results)} relevant chunks.")

    return results


def main():
    print("\n" + "#" * 65)
    print("STANDALONE RAG RETRIEVAL TEST SUITE (PINECONE + NVIDIA NIM)")
    print("#" * 65)

    test_queries = [
        # Query 1: Location of search logic
        "Where is the search performed in the code?",
        # Query 2: Location of vector database / Pinecone setup
        "Where is the Pinecone index initialized or created?",
        # Query 3: Chunking logic
        "Where is the document chunking or text splitting implemented?",
        # Query 4: Negative Test (Out of scope - should trigger 'I could not find that')
        "Where is the user authentication and OAuth login JWT token verified?",
    ]

    for q in test_queries:
        search_codebase(query=q, top_k=3, score_threshold=config.similarity_threshold)


if __name__ == "__main__":
    main()
