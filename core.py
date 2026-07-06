import os
import re
import glob
import logging
import chromadb
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load API key and environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logging.warning("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
else:
    genai.configure(api_key=api_key)

# Hardened System Prompt for Cohort IQ
SYSTEM_PROMPT = """You are Cohort IQ, an intelligent course companion.
You help AI Engineering interns by answering questions about their coursework.

CRITICAL RULES:
1. Answer the user's question using ONLY the provided context chunks.
2. If the answer is not in the context, say 'I don't have that information in the course notes.' Do not make up any facts.
3. Be factual, technical, and precise.
4. Do NOT put inline citations like '(Day 12)' or '[Day 1]' inside the sentences. Write a clean, natural response. The application will list the sources at the end.
5. If the question asks for a comparison, structure your answer to directly contrast the relevant topics (highlighting similarities, differences, or how they build on each other).
"""

# Mapping of core keywords to their respective Day numbers for range queries
TOPIC_DAYS = {
    "python": 1,
    "chunking": 8,
    "ui": 9,
    "streamlit": 9,
    "agent": 10,
    "safety": 12,
    "guardrail": 12,
    "evaluation": 13,
    "deployment": 14
}

def get_embed_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def get_chroma_client():
    return chromadb.PersistentClient(path="chroma_db")

def chunk_markdown_file(filepath: str, max_chunk_len: int = 300) -> list[dict]:
    filename = os.path.basename(filepath)
    day_match = re.search(r"day\s*(\d+)", filename, re.IGNORECASE)
    day_name = f"Day {day_match.group(1)}" if day_match else filename.replace(".md", "")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.split("\n\n")
    chunks = []
    current_header = "Introduction"
    
    current_chunk_text = []
    current_len = 0
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        if block.startswith("#") and not block.startswith("## →"):
            if current_chunk_text:
                chunk_content = "\n\n".join(current_chunk_text)
                chunks.append({
                    "text": f"[{day_name} - {current_header}]\n{chunk_content}",
                    "metadata": {"day": day_name, "header": current_header, "file": filename}
                })
                current_chunk_text = []
                current_len = 0
            current_header = block.strip("# ")
            continue
            
        block_len = len(block.split())
        
        if current_len + block_len > max_chunk_len and current_chunk_text:
            chunk_content = "\n\n".join(current_chunk_text)
            chunks.append({
                "text": f"[{day_name} - {current_header}]\n{chunk_content}",
                "metadata": {"day": day_name, "header": current_header, "file": filename}
            })
            current_chunk_text = [block]
            current_len = block_len
        else:
            current_chunk_text.append(block)
            current_len += block_len
            
    if current_chunk_text:
        chunk_content = "\n\n".join(current_chunk_text)
        chunks.append({
            "text": f"[{day_name} - {current_header}]\n{chunk_content}",
            "metadata": {"day": day_name, "header": current_header, "file": filename}
        })
        
    return chunks

def index_documents(data_dir: str = "data"):
    embed_model = get_embed_model()
    client = get_chroma_client()
    collection = client.get_or_create_collection("cohort_iq_lessons")
    
    if collection.count() > 0:
        logging.info(f"Database already populated with {collection.count()} chunks. Skipping indexing.")
        return collection
        
    md_files = glob.glob(os.path.join(data_dir, "*.md"))
    if not md_files:
        logging.warning(f"No markdown files (.md) found in '{data_dir}/' directory.")
        return collection
        
    all_chunks = []
    for filepath in md_files:
        logging.info(f"Parsing {filepath}...")
        all_chunks.extend(chunk_markdown_file(filepath))
        
    if not all_chunks:
        return collection
        
    logging.info(f"Embedding and indexing {len(all_chunks)} chunks...")
    
    documents = [c["text"] for c in all_chunks]
    embeddings = embed_model.encode(documents).tolist()
    metadatas = [c["metadata"] for c in all_chunks]
    ids = [f"chunk_{i}" for i in range(len(all_chunks))]
    
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    
    logging.info(f"Successfully indexed {len(all_chunks)} chunks.")
    return collection

def query_pipeline(question: str, collection, embed_model, llm) -> tuple[str, list[dict]]:
    if collection.count() == 0:
        return "The database is empty. Please add markdown files into the 'data/' directory to get started.", []
        
    # 1. Check for specific Day numbers in the query
    day_matches = re.findall(r"day\s*(\d+)", question, re.IGNORECASE)
    where_clause = None
    
    if day_matches:
        day_nums = [int(num) for num in day_matches]
        if len(day_nums) == 1:
            target_day = f"Day {day_nums[0]:02d}"
            where_clause = {"day": target_day}
            logging.info(f"Applying metadata filter: {where_clause}")
        else:
            where_clause = {"$or": [{"day": f"Day {num:02d}"} for num in day_nums]}
            logging.info(f"Applying multi-day metadata filter: {where_clause}")
            
    # 2. Topic Range query (e.g. "between chunking and deployment")
    else:
        found_topics = []
        for topic, day_num in TOPIC_DAYS.items():
            if topic in question.lower():
                found_topics.append((topic, day_num))
                
        if len(found_topics) >= 2:
            found_topics.sort(key=lambda x: x[1])
            start_day = found_topics[0][1]
            end_day = found_topics[-1][1]
            
            days_range = [f"Day {i:02d}" for i in range(start_day, end_day + 1)]
            logging.info(f"Applying round-robin range query for: {days_range}")
            
            # Query exactly 1 chunk from EACH day in the range to ensure complete diversity
            query_vector = embed_model.encode([question]).tolist()
            retrieved_docs = []
            metadatas = []
            
            for d in days_range:
                results = collection.query(
                    query_embeddings=query_vector,
                    n_results=1,
                    where={"day": d}
                )
                if results["documents"][0]:
                    retrieved_docs.append(results["documents"][0][0])
                    metadatas.append(results["metadatas"][0][0])
                    
            context = "\n\n".join(retrieved_docs)
            prompt = f"Context from course notes:\n{context}\n\nQuestion: {question}"
            response = llm.generate_content(prompt)
            return response.text.strip(), metadatas
    
    # 3. Standard semantic query (if not a range query)
    query_vector = embed_model.encode([question]).tolist()
    n_results = min(8, collection.count())
    
    results = collection.query(
        query_embeddings=query_vector,
        n_results=n_results,
        where=where_clause
    )
    
    retrieved_docs = results["documents"][0]
    metadatas = results["metadatas"][0]
    
    context = "\n\n".join(retrieved_docs)
    prompt = f"Context from course notes:\n{context}\n\nQuestion: {question}"
    
    response = llm.generate_content(prompt)
    return response.text.strip(), metadatas

def main():
    print("=" * 60)
    print("      Cohort IQ: Core RAG Pipeline Terminal Session")
    print("=" * 60)
    
    if not os.path.exists("data"):
        os.makedirs("data")
        
    collection = index_documents()
    
    if collection.count() == 0:
        print("\n⚠️ No coursework data loaded. Please add markdown files to the 'data' folder and run this again.")
        return
        
    print("Loading models...")
    embed_model = get_embed_model()
    llm = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    
    print("\n✅ Core engine loaded successfully. Type 'exit' or 'quit' to end session.")
    print("-" * 60)
    
    while True:
        try:
            question = input("\nAsk a question about the course: ").strip()
            if not question:
                continue
            if question.lower() in ["exit", "quit"]:
                print("Exiting pipeline session.")
                break
                
            print("Thinking...")
            answer, sources = query_pipeline(question, collection, embed_model, llm)
            
            print("\n💡 ANSWER:")
            print(answer)
            
            print("\n📖 CITATIONS:")
            unique_days = sorted(list(set(s["day"] for s in sources)))
            for day in unique_days:
                print(f"- {day}")
                
        except KeyboardInterrupt:
            print("\nExiting pipeline session.")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()