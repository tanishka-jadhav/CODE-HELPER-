"""
test_pinecone.py — Pre-flight verification for Pinecone Serverless Vector DB.
Ensures connection works and the 'code-helper' index is provisioned
with dimension=2048 and metric='cosine'.
"""
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# 1. Load .env
root_dir = Path(__file__).resolve().parent.parent
env_file = root_dir / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

# 2. Check Pinecone credentials (without printing secrets)
api_key = os.getenv("PINECONE_API_KEY", "").strip()
if not api_key or "your-pinecone-api-key" in api_key:
    print("[ERROR] PINECONE_API_KEY not found or set to placeholder in .env!")
    sys.exit(1)

index_name = os.getenv("PINECONE_INDEX_NAME", "code-helper").strip()
cloud = os.getenv("PINECONE_CLOUD", "aws").strip()
region = os.getenv("PINECONE_REGION", "us-east-1").strip()
dimension = 2048
metric = "cosine"

print("=" * 60)
print("PRE-FLIGHT CHECK: PINECONE VECTOR DATABASE")
print("=" * 60)
print(f"[*] Target Index : {index_name}")
print(f"[*] Cloud / Reg  : {cloud.upper()} ({region})")
print(f"[*] Dimension    : {dimension}")
print(f"[*] Metric       : {metric}")
print(f"[*] Key Status   : PRESENT (Masked per Security Policy)")

try:
    pc = Pinecone(api_key=api_key)
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    print(f"[*] Existing indexes in account: {existing_indexes}")

    if index_name not in existing_indexes:
        print(f"[*] Index '{index_name}' does not exist. Creating Serverless Index...")
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(cloud=cloud, region=region),
        )
        print(f"[*] Index creation initiated. Waiting for readiness...")
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(2)
        print(f"[OK] Index '{index_name}' successfully created and ready!")
    else:
        desc = pc.describe_index(index_name)
        print(f"[OK] Index '{index_name}' already exists.")
        print(f"[*] Existing Index Dimension : {desc.dimension}")
        print(f"[*] Existing Index Metric    : {desc.metric}")
        print(f"[*] Index Host               : {desc.host}")
        
        if desc.dimension != dimension:
            print(f"[CRITICAL ERROR] Index dimension is {desc.dimension}, but model requires {dimension}!")
            print(f"Please delete index '{index_name}' from Pinecone console or rename PINECONE_INDEX_NAME.")
            sys.exit(1)
        if desc.metric != metric:
            print(f"[WARNING] Index metric is {desc.metric}, but assignment specifies {metric}.")

    # Quick index stats check
    idx = pc.Index(index_name)
    stats = idx.describe_index_stats()
    print("\n" + "-" * 60)
    print(f"[VERIFIED] Pinecone connection successful and index is ACTIVE.")
    print(f"[*] Total Vectors currently indexed : {stats.total_vector_count}")
    print("-" * 60 + "\n")

except Exception as err:
    print(f"\n[ERROR] Failed to connect to Pinecone: {err}")
    sys.exit(1)
