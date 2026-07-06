import os
import glob
from dotenv import load_dotenv
import google.generativeai as genai
from core import (
    chunk_markdown_file, 
    get_embed_model, 
    get_chroma_client, 
    query_pipeline
)

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def run_tests():
    data_dir = "data"
    
    # ── STAGE 1: Load and Chunk ──────────────────────────────────────────────
    print("=== Stage 1: Load and chunk documents ===")
    md_files = glob.glob(os.path.join(data_dir, "*.md"))
    if not md_files:
        print(f"❌ Error: Please place at least one markdown file (.md) in your '{data_dir}' folder before running.")
        return
        
    all_chunks = []
    for filepath in md_files:
        all_chunks.extend(chunk_markdown_file(filepath))
        
    print(f"Loaded {len(md_files)} files, produced {len(all_chunks)} chunks.")
    if all_chunks:
        print(f'Sample chunk:\n"{all_chunks[0]["text"][:150]}..."')
    print()

    # ── STAGE 2: Embed and Store ──────────────────────────────────────────────
    print("=== Stage 2: Embed and store ===")
    embed_model = get_embed_model()
    client = get_chroma_client()
    
    # Delete old test collection to force a fresh index for this test run
    try:
        client.delete_collection("cohort_iq_lessons")
    except:
        pass
        
    collection = client.get_or_create_collection("cohort_iq_lessons")
    
    documents = [c["text"] for c in all_chunks]
    embeddings = embed_model.encode(documents).tolist()
    metadatas = [c["metadata"] for c in all_chunks]
    ids = [f"test_chunk_{i}" for i in range(len(all_chunks))]
    
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Stored {len(all_chunks)} chunks in Chroma collection 'cohort_iq_lessons'.")
    print(f"Collection count: {collection.count()}")
    print()

    # ── STAGE 3: Retrieve ────────────────────────────────────────────────────
    print("=== Stage 3: Retrieve ===")
    test_query = "What did we learn on Day 12?"
    print(f'Query: "{test_query}"')
    
    query_vector = embed_model.encode([test_query]).tolist()
    results = collection.query(
        query_embeddings=query_vector,
        n_results=1
    )
    
    if results["documents"][0]:
        top_result = results["documents"][0][0]
        # Calculate a mock similarity distance
        distance = results["distances"][0][0] if "distances" in results and results["distances"] else 0.0
        print(f'Top result: "{top_result[:150]}..."')
        print(f"(distance: {round(distance, 4)})")
    else:
        print("❌ No matching chunks found.")
    print()

    # ── STAGE 4: Generate ────────────────────────────────────────────────────
    print("=== Stage 4: Generate ===")
    llm = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=(
            "You are Cohort IQ. Answer the question using ONLY the provided context chunks. "
            "If the answer is not in the context, say 'I don't have that info.' Cite the source Day."
        )
    )
    
    answer, sources = query_pipeline(test_query, collection, embed_model, llm)
    print(f'Question: "{test_query}"')
    print(f"Answer: {answer}")

if __name__ == "__main__":
    run_tests()