"""
code_helper/index_codebase.py — 5-Step Manual RAG Indexing Pipeline.

Implements the offline indexing stages from scratch (No LangChain, No LlamaIndex):
  1. Read  : Ingests all .py files in Naive_RAG/
  2. Split : Sliding window chunking with line-number provenance
  3. Embed : Batched high-throughput embedding via NVIDIA NIM (2048 dims)
  4. Store : Upsert vectors and rich metadata to Pinecone Serverless
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


def read_codebase(target_dir: Path) -> list[dict]:
    """
    Stage 1: Read
    Scans the target directory and loads all .py files with UTF-8 encoding.
    """
    print("\n" + "=" * 65)
    print("STAGE 1: CODEBASE INGESTION (READ)")
    print("=" * 65)
    print(f"[*] Target Directory: {target_dir.resolve()}")

    if not target_dir.exists():
        raise FileNotFoundError(f"Target directory does not exist: {target_dir}")

    files_data = []
    py_files = sorted(list(target_dir.glob("*.py")))

    if not py_files:
        print("[!] No .py files found in target directory!")
        return []

    for file_path in py_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        line_count = len(content.splitlines())
        char_count = len(content)
        relative_path = file_path.relative_to(PROJECT_ROOT).as_posix()

        files_data.append({
            "file_name": file_path.name,
            "relative_path": relative_path,
            "absolute_path": str(file_path.resolve()),
            "content": content,
            "line_count": line_count,
            "char_count": char_count,
        })
        print(f"  -> Ingested: {file_path.name:<20} ({line_count:>4} lines, {char_count:>5} chars)")

    print(f"[OK] Ingested {len(files_data)} Python files successfully.")
    return files_data


def split_into_chunks(files_data: list[dict], chunk_size: int, chunk_overlap: int) -> list[dict]:
    """
    Stage 2: Split (Chunking)
    Slices each file into overlapping chunks while computing exact line ranges.
    """
    print("\n" + "=" * 65)
    print("STAGE 2: CHUNKING (SLIDING WINDOW WITH LINE TRACKING)")
    print("=" * 65)
    print(f"[*] Chunk Size    : {chunk_size} characters")
    print(f"[*] Chunk Overlap : {chunk_overlap} characters")
    print(f"[*] Stride / Step : {chunk_size - chunk_overlap} characters")

    step = chunk_size - chunk_overlap
    all_chunks = []

    for file_info in files_data:
        text = file_info["content"]
        file_name = file_info["file_name"]
        relative_path = file_info["relative_path"]

        # Precompute line start offsets for fast line number translation
        lines = text.splitlines(keepends=True)
        line_start_offsets = []
        curr_offset = 0
        for line in lines:
            line_start_offsets.append(curr_offset)
            curr_offset += len(line)

        def offset_to_line(offset: int) -> int:
            for idx, start_pos in enumerate(line_start_offsets):
                if offset < start_pos:
                    return max(1, idx)
            return len(lines)

        start = 0
        file_chunk_idx = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_raw = text[start:end]
            chunk_clean = chunk_raw.strip()

            if chunk_clean:
                start_line = offset_to_line(start)
                end_line = offset_to_line(end)

                chunk_id = f"{file_name}#c{file_chunk_idx}"
                all_chunks.append({
                    "id": chunk_id,
                    "file_name": file_name,
                    "file_path": relative_path,
                    "start_line": start_line,
                    "end_line": max(start_line, end_line),
                    "text": chunk_clean,
                })
                file_chunk_idx += 1

            if end >= len(text):
                break
            start += step

        print(f"  -> {file_name:<20}: Created {file_chunk_idx:>2} chunks")

    print(f"[OK] Total discrete chunks created across codebase: {len(all_chunks)}")
    return all_chunks


def embed_chunks(chunks: list[dict], batch_size: int = 16) -> list[dict]:
    """
    Stage 3: Embed (NVIDIA NIM)
    Batch-embeds chunks using nvidia/nemotron-3-embed-1b.
    """
    print("\n" + "=" * 65)
    print("STAGE 3: BATCH EMBEDDING (NVIDIA NIM)")
    print("=" * 65)
    print(f"[*] Embedding Model : {config.embed_model}")
    print(f"[*] Target Dimension: {config.embed_dimension}")
    print(f"[*] Total Chunks    : {len(chunks)}")
    print(f"[*] Batch Size      : {batch_size}")

    client = OpenAI(
        base_url=config.nvidia_base_url,
        api_key=config.nvidia_api_key,
    )

    enriched_chunks = []
    total = len(chunks)

    for i in range(0, total, batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c["text"] for c in batch]

        print(f"[*] Embedding batch {i // batch_size + 1} ({len(texts)} chunks)...")
        response = client.embeddings.create(
            input=texts,
            model=config.embed_model,
        )

        for item, orig in zip(response.data, batch):
            enriched = dict(orig)
            enriched["embedding"] = item.embedding
            enriched_chunks.append(enriched)

    print(f"[OK] Generated {len(enriched_chunks)} vectors from NVIDIA NIM successfully.")
    return enriched_chunks


def store_in_pinecone(chunks_with_embeddings: list[dict], batch_size: int = 50) -> int:
    """
    Stage 4: Store (Pinecone Serverless)
    Upserts vectors with full line provenance and code text in metadata.
    """
    print("\n" + "=" * 65)
    print("STAGE 4: STORAGE IN PINECONE SERVERLESS")
    print("=" * 65)
    print(f"[*] Pinecone Index : {config.pinecone_index_name}")

    pc = Pinecone(api_key=config.pinecone_api_key)
    index = pc.Index(config.pinecone_index_name)

    vectors_payload = []
    for item in chunks_with_embeddings:
        record = {
            "id": item["id"],
            "values": item["embedding"],
            "metadata": {
                "file_name": item["file_name"],
                "file_path": item["file_path"],
                "start_line": item["start_line"],
                "end_line": item["end_line"],
                "text": item["text"],
            },
        }
        vectors_payload.append(record)

    # Upsert in batches
    total_upserted = 0
    for i in range(0, len(vectors_payload), batch_size):
        batch = vectors_payload[i : i + batch_size]
        index.upsert(vectors=batch)
        total_upserted += len(batch)
        print(f"  -> Upserted vectors {i + 1} to {min(i + batch_size, len(vectors_payload))}...")

    # Verification of index stats
    time.sleep(2)  # Allow indexing pipeline to commit
    stats = index.describe_index_stats()
    print("\n" + "-" * 65)
    print(f"[SUCCESS] Pinecone Indexing Complete!")
    print(f"[*] Current Total Vectors in Index : {stats.total_vector_count}")
    print("-" * 65)
    return total_upserted


def run_indexing():
    """Execute the end-to-end 4-stage pipeline."""
    start_time = time.time()
    print("\n" + "#" * 65)
    print("STARTING MANUAL 5-STEP RAG INDEXING PIPELINE (CODEBASE)")
    print("#" * 65)

    # 1. Read
    files = read_codebase(config.target_codebase_dir)
    if not files:
        sys.exit(1)

    # 2. Split
    chunks = split_into_chunks(
        files_data=files,
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
    )

    # 3. Embed
    embedded_chunks = embed_chunks(chunks)

    # 4. Store
    store_in_pinecone(embedded_chunks)

    elapsed = round(time.time() - start_time, 2)
    print(f"\n[DONE] Pipeline finished in {elapsed} seconds. Knowledge base is ready!\n")


if __name__ == "__main__":
    run_indexing()
