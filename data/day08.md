## **Day 8 — Chunking & Citing Sources** 

Your RAG pipeline works. Today you make it more accurate — and trustworthy. 

**What you're bringing in:** the full RAG pipeline from Day 7 — load, chunk, embed, store, retrieve, generate. Today you replace the naive chunker with better strategies, and add source citations to every answer. 

## **1. Why Chunking Matters** 

## **The chunk is the unit of retrieval** 

When a user asks a question, your pipeline retrieves chunks — not whole documents. The chunk that comes back either contains the answer or it doesn't. Chunking strategy is therefore one of the biggest levers you have on answer quality. 

Get it wrong in two directions: 

**Too large:** The chunk contains the answer, but also a lot of irrelevant text. The model's attention gets diluted. Answers become vague or miss the specific detail the user needed. 

**Too small:** Each chunk is a single sentence. It may not have enough context to be useful on its own. A sentence like "It was introduced in 1991." is useless without knowing what "it" refers to. 

**The goal:** chunks that are small enough to be specific, large enough to be self-contained. 

## **The three strategies you'll compare today** 

**Fixed-size chunking** — split by a fixed number of characters or sentences, regardless of content structure. Simple, predictable, but can cut sentences mid-thought. 

**Sentence chunking** — split on sentence boundaries, group N sentences per chunk. Cleaner than fixed-size, respects natural language structure. 

**Overlapping chunking** — same as sentence chunking, but consecutive chunks share some sentences. If the answer spans a boundary between two chunks, overlap ensures at least one chunk contains most of it. 

## **2. Fixed-Size Chunking** 

Split text into chunks of exactly N characters, with no regard for sentence boundaries. 

def fixed_size_chunks(text, chunk_size=300): 

text = text.strip() 

return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)] 

Simple and fast. The main drawback is that it cuts sentences mid-way, which can produce chunks that start or end in the middle of a thought. 

## **Exercise — See what fixed-size chunks look like** 

## **Exercise 1 — Inspect the chunk boundaries** 

text = """ 

Python was created by Guido van Rossum and first released in 1991. It is an interpreted, high-level, general-purpose programming language. Python's design philosophy emphasises code readability and simplicity. 

It supports multiple programming paradigms including procedural, object-oriented, and functional programming. 

Python has a large standard library and an active community. 

It is widely used in web development, data science, machine learning, and automation. The name Python comes from the BBC television show Monty Python's Flying Circus. Python 2 reached end of life in 2020 and Python 3 is the current standard. Popular Python frameworks include Django and Flask for web development. NumPy, Pandas, and Scikit-learn are widely used for data science work. TensorFlow and PyTorch are the dominant libraries for deep learning in Python. Python is consistently ranked as one of the most popular programming languages in the world. 

""".strip() 

def fixed_size_chunks(text, chunk_size=200): return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)] 

chunks = fixed_size_chunks(text, chunk_size=200) 

print(f"Fixed-size chunking (200 chars) → {len(chunks)} chunks\n") for i, chunk in enumerate(chunks): print(f"--- Chunk {i} ---") print(repr(chunk)) print() 

Look at the chunk boundaries. Do any chunks start mid-sentence? Does that affect readability? Would a retrieval system be able to use a chunk that starts with "rk. NumPy, Pandas"? 

## **3. Sentence Chunking** 

Split on sentence boundaries, then group N sentences per chunk. Much cleaner than fixed-size. 

def sentence_chunks(text, sentences_per_chunk=3): 

sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()] 

chunks = [] 

for i in range(0, len(sentences), sentences_per_chunk): 

group = sentences[i:i + sentences_per_chunk] chunks.append(". ".join(group) + ".") 

return chunks 

## **Exercise — Compare fixed-size vs sentence chunks** 

## **Exercise 2 — Same text, two strategies, side by side** 

def fixed_size_chunks(text, chunk_size=200): 

return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)] 

def sentence_chunks(text, sentences_per_chunk=3): 

sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()] chunks = [] 

for i in range(0, len(sentences), sentences_per_chunk): 

group = sentences[i:i + sentences_per_chunk] chunks.append(". ".join(group) + ".") 

return chunks 

text = """ 

Python was created by Guido van Rossum and first released in 1991. It is an interpreted, high-level, general-purpose programming language. Python's design philosophy emphasises code readability and simplicity. 

It supports multiple programming paradigms including procedural, object-oriented, and functional programming. 

Python has a large standard library and an active community. 

It is widely used in web development, data science, machine learning, and automation. The name Python comes from the BBC television show Monty Python's Flying Circus. Python 2 reached end of life in 2020 and Python 3 is the current standard. Popular Python frameworks include Django and Flask for web development. NumPy, Pandas, and Scikit-learn are widely used for data science work. TensorFlow and PyTorch are the dominant libraries for deep learning in Python. Python is consistently ranked as one of the most popular programming languages in the world. 

""".strip() 

fixed = fixed_size_chunks(text, chunk_size=200) 

sentence = sentence_chunks(text, sentences_per_chunk=3) 

print(f"Fixed-size:  {len(fixed)} chunks") print(f"Sentence:    {len(sentence)} chunks\n") 

print("=== Fixed-size ===") for i, c in enumerate(fixed): print(f"[{i}] {c}\n") print("=== Sentence ===") for i, c in enumerate(sentence): print(f"[{i}] {c}\n") 

Which chunks look more usable? Which would you rather have returned as a source passage to show a user? 

## **4. Overlapping Chunking** 

Consecutive chunks share some sentences. This means an answer that falls near a boundary will be fully captured in at least one chunk. 

def overlapping_chunks(text, sentences_per_chunk=3, overlap=1): sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()] chunks = [] step = sentences_per_chunk - overlap for i in range(0, len(sentences), step): group = sentences[i:i + sentences_per_chunk] if group: chunks.append(". ".join(group) + ".") return chunks 

With sentences_per_chunk=3 and overlap=1 , chunk 0 covers sentences 0–2, chunk 1 covers sentences 1–3, chunk 2 covers sentences 2–4, and so on. Every sentence appears in multiple chunks. 

The tradeoff: more chunks to store and search, but better coverage of boundary-spanning answers. 

## **Exercise — See overlap in action** 

## **Exercise 3 — Print overlapping chunks and highlight the shared sentences** 

def overlapping_chunks(text, sentences_per_chunk=3, overlap=1): sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()] 

chunks = [] 

step = sentences_per_chunk - overlap 

for i in range(0, len(sentences), step): 

group = sentences[i:i + sentences_per_chunk] 

if group: 

chunks.append(". ".join(group) + ".") 

return chunks 

text = """ 

Python was created by Guido van Rossum and first released in 1991. It is an interpreted, high-level, general-purpose programming language. Python's design philosophy emphasises code readability and simplicity. 

It supports multiple programming paradigms including procedural, object-oriented, and functional programming. 

Python has a large standard library and an active community. 

It is widely used in web development, data science, machine learning, and automation. """.strip() 

chunks = overlapping_chunks(text, sentences_per_chunk=3, overlap=1) 

print(f"Overlapping chunks (3 sentences, overlap=1) → {len(chunks)} chunks\n") for i, chunk in enumerate(chunks): 

print(f"--- Chunk {i} ---") print(chunk) print() 

Compare the number of chunks here versus the non-overlapping sentence chunker from Exercise 2. Which sentences appear in more than one chunk? 

## **5. Comparing Strategies on a Real Query** 

Knowing the theory is one thing. The real test is whether different chunking strategies produce different answers to the same question. 

## **Exercise — Three chunkers, one question, compare answers** 

## **Exercise 4 — Run all three strategies through the full RAG pipeline** 

import os 

import chromadb import google.generativeai as genai from sentence_transformers import SentenceTransformer from dotenv import load_dotenv 

load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

embed_model = SentenceTransformer("all-MiniLM-L6-v2") llm = genai.GenerativeModel( 

model_name="gemini-1.5-flash", system_instruction=( "Answer using only the context provided. " 

"If the answer is not in the context, say 'I don't have that information.'" ), 

) 

document = """ 

Python was created by Guido van Rossum and first released in 1991. It is an interpreted, high-level, general-purpose programming language. Python's design philosophy emphasises code readability and simplicity. It supports multiple programming paradigms including procedural, object-oriented, and functional programming. 

Python has a large standard library and an active community. 

It is widely used in web development, data science, machine learning, and automation. The name Python comes from the BBC television show Monty Python's Flying Circus. Python 2 reached end of life in 2020 and Python 3 is the current standard. Popular Python frameworks include Django and Flask for web development. NumPy, Pandas, and Scikit-learn are widely used for data science work. TensorFlow and PyTorch are the dominant libraries for deep learning in Python. 

Python is consistently ranked as one of the most popular programming languages in the world. 

""".strip() 

def fixed_size_chunks(text, chunk_size=200): 

return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)] 

def sentence_chunks(text, n=3): sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()] return [". ".join(sentences[i:i+n]) + "." for i in range(0, len(sentences), n)] 

def overlapping_chunks(text, n=3, overlap=1): sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()] step = n - overlap chunks = [] for i in range(0, len(sentences), step): group = sentences[i:i + n] if group: 

chunks.append(". ".join(group) + ".") return chunks 

def build_rag(chunks, collection_name): client = chromadb.Client() collection = client.create_collection(collection_name) embeddings = embed_model.encode(chunks).tolist() ids = [f"c_{i}" for i in range(len(chunks))] collection.add(documents=chunks, embeddings=embeddings, ids=ids) return collection 

def rag_answer(question, collection): results = collection.query( query_embeddings=embed_model.encode([question]).tolist(), n_results=3, ) chunks = results["documents"][0] context = "\n\n".join(f"- {c}" for c in chunks) prompt = f"Context:\n{context}\n\nQuestion: {question}" return llm.generate_content(prompt).text.strip(), chunks 

strategies = { "Fixed-size (200 chars)":        fixed_size_chunks(document, chunk_size=200), "Sentence (3 per chunk)":        sentence_chunks(document, n=3), "Overlapping (3 sent, overlap 1)": overlapping_chunks(document, n=3, overlap=1), } 

question = "What libraries are used for deep learning in Python?" 

print(f"Question: {question}\n") print("=" * 60) 

for strategy_name, chunks in strategies.items(): collection = build_rag(chunks, strategy_name.replace(" ", "_")[:30]) answer, used_chunks = rag_answer(question, collection) 

print(f"\nStrategy: {strategy_name} ({len(chunks)} chunks)") print(f"Answer: {answer}") print(f"Top retrieved chunk: {used_chunks[0][:120]}...") print("-" * 60) 

Do all three strategies find the right answer? Is any strategy cleaner or more precise? Look at the top retrieved chunk for each — does a better chunk lead to a better answer? 

## **6. Citing Sources** 

## **Why citations matter** 

Without citations, users have no way to verify an answer. An AI that says "TensorFlow and PyTorch are the dominant libraries" is less trustworthy than one that says the same thing and shows you exactly which passage it drew from. Citations also help you debug — if the answer is wrong, you can check whether the right chunk was retrieved. 

## **What to return** 

Your RAG function already returns the chunks it used. The change is small: surface them to the user alongside the answer. 

def rag_with_citations(question, collection): results = collection.query( query_embeddings=embed_model.encode([question]).tolist(), n_results=3, ) chunks = results["documents"][0] context = "\n\n".join(f"- {c}" for c in chunks) prompt = f"Context:\n{context}\n\nQuestion: {question}" answer = llm.generate_content(prompt).text.strip() return answer, chunks 

The returned chunks are the citations. Display them clearly beneath the answer. 

## **Exercise — Display citations cleanly** 

## **Exercise 5 — Format answers with their source passages** 

import os import chromadb import google.generativeai as genai from sentence_transformers import SentenceTransformer from dotenv import load_dotenv 

load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

embed_model = SentenceTransformer("all-MiniLM-L6-v2") llm = genai.GenerativeModel( model_name="gemini-1.5-flash", system_instruction=( "Answer using only the context provided. " 

"If the answer is not in the context, say 'I don't have that information.'" ), ) 

document = """ Python was created by Guido van Rossum and first released in 1991. It is an interpreted, high-level, general-purpose programming language. Python's design philosophy emphasises code readability and simplicity. It supports multiple programming paradigms including procedural, object-oriented, and functional programming. Python has a large standard library and an active community. It is widely used in web development, data science, machine learning, and automation. The name Python comes from the BBC television show Monty Python's Flying Circus. Python 2 reached end of life in 2020 and Python 3 is the current standard. Popular Python frameworks include Django and Flask for web development. NumPy, Pandas, and Scikit-learn are widely used for data science work. TensorFlow and PyTorch are the dominant libraries for deep learning in Python. Python is consistently ranked as one of the most popular programming languages in the world. """.strip() 

def sentence_chunks(text, n=3): sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()] return [". ".join(sentences[i:i+n]) + "." for i in range(0, len(sentences), n)] 

chunks = sentence_chunks(document) client = chromadb.Client() collection = client.create_collection("cited_rag") collection.add( documents=chunks, embeddings=embed_model.encode(chunks).tolist(), ids=[f"c_{i}" for i in range(len(chunks))], ) 

def rag_with_citations(question): results = collection.query( query_embeddings=embed_model.encode([question]).tolist(), n_results=3, ) used_chunks = results["documents"][0] context = "\n\n".join(f"- {c}" for c in used_chunks) prompt = f"Context:\n{context}\n\nQuestion: {question}" answer = llm.generate_content(prompt).text.strip() return answer, used_chunks 

def display(question, answer, sources): print(f"Question: {question}") print(f"\nAnswer:\n{answer}") 

print(f"\nSources used ({len(sources)}):") for i, source in enumerate(sources, 1): print(f"  [{i}] {source}") print("\n" + "=" * 60 + "\n") 

questions = [ "Who created Python and when?", "What is Python used for?", "What libraries exist for deep learning?", "What is the capital of Pakistan?", ] 

for q in questions: answer, sources = rag_with_citations(q) display(q, answer, sources) 

Look at the last question. The answer should say it doesn't have that information — and the sources shown should make it obvious why: none of them contain anything about Pakistan. 

## **Exercise — Interactive cited RAG** 

## **Exercise 6 — Build an interactive loop with citations** 

Put everything together into a script the user can run and ask questions to. After each answer, show the sources. 

import os import chromadb import google.generativeai as genai from sentence_transformers import SentenceTransformer from dotenv import load_dotenv 

load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

embed_model = SentenceTransformer("all-MiniLM-L6-v2") llm = genai.GenerativeModel( model_name="gemini-1.5-flash", system_instruction=( "Answer using only the context provided. " "If the answer is not in the context, say 'I don't have that information.'" ), ) 

def overlapping_chunks(text, n=3, overlap=1): 

sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()] step = n - overlap chunks = [] for i in range(0, len(sentences), step): group = sentences[i:i + n] if group: chunks.append(". ".join(group) + ".") return chunks def load_and_index(filepath): with open(filepath, "r", encoding="utf-8") as f: text = f.read() chunks = overlapping_chunks(text, n=3, overlap=1) client = chromadb.Client() collection = client.create_collection("interactive_rag") collection.add( documents=chunks, embeddings=embed_model.encode(chunks).tolist(), ids=[f"c_{i}" for i in range(len(chunks))], ) return collection, len(chunks) 

def ask(question, collection): results = collection.query( query_embeddings=embed_model.encode([question]).tolist(), n_results=3, ) used_chunks = results["documents"][0] context = "\n\n".join(f"- {c}" for c in used_chunks) prompt = f"Context:\n{context}\n\nQuestion: {question}" answer = llm.generate_content(prompt).text.strip() return answer, used_chunks 

collection, total_chunks = load_and_index("knowledge.txt") print(f"Loaded knowledge.txt — {total_chunks} chunks indexed.\n") print("Ask questions. Type 'quit' to exit.\n") 

while True: question = input("Q: ").strip() if not question: continue if question.lower() == "quit": break answer, sources = ask(question, collection) print(f"\nA: {answer}\n") print("Sources:") for i, source in enumerate(sources, 1): 

print(f"  [{i}] {source[:120]}...") print() 

This is meaningfully better than the Day 7 pipeline — overlapping chunks reduce missed answers at boundaries, and every answer now shows exactly where it came from. 

## **Check Your Understanding** 

Before moving to Day 9, make sure you can answer these without looking: 

1. A chunk contains the answer but also three unrelated paragraphs. What problem does this cause, and which chunking strategy helps? 

2. A question asks about something that spans the boundary between two consecutive chunks. Which chunking strategy is most likely to retrieve a useful result? 

3. You retrieve the perfect chunk but the answer is still wrong. Where is the failure — retrieval or generation? 

4. Why is returning source citations better than returning just the answer, from both a user trust and a debugging perspective? 

5. A user asks a question not covered in the document, but the model answers confidently anyway. What is missing from your pipeline? 

