## **Day 6 — Vector Databases with Chroma** 

You know how to create embeddings. Today you learn where to store them — and how to search them at scale. 

**What you're bringing in:** embeddings, cosine similarity, Sentence Transformers (Day 5). A vector database is just a smarter place to store and search the vectors you already know how to make. 

## **1. Why Vector Databases Exist** 

## **The problem with plain lists** 

On Day 5 you stored embeddings in a NumPy array and searched by computing cosine similarity against every single entry. That works fine for 20 sentences. It breaks down at scale: 

- 10,000 documents → 10,000 similarity calculations per query 

- 1,000,000 documents → too slow to be usable 

- After your script exits → everything is gone, you have to re-embed everything next time 

A vector database solves all three problems: it stores vectors on disk so they persist, and it uses indexing to find similar vectors fast without comparing against everything. 

## **What Chroma is** 

Chroma is a free, open-source vector database that runs locally with no setup beyond pip install . For learning and for small-to-medium applications, it's the right tool. You don't need a server, a cloud account, or a credit card. 

pip install chromadb 

## **The three things you'll always do** 

import chromadb 

# 1. Create a client (in-memory by default) client = chromadb.Client() 

# 2. Create a collection (like a table in a regular database) collection = client.create_collection("my_collection") 

# 3. Add documents, embeddings, and IDs collection.add( documents=["text one", "text two"], embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]], ids=["id1", "id2"], ) 

# 4. Query results = collection.query( query_embeddings=[[0.15, 0.25, ...]], n_results=2, ) 

Chroma stores your documents alongside their vectors, so when you query you get the original text back — not just IDs. 

## **Exercise — Your first Chroma collection** 

## **Exercise 1 — Add documents and run your first query** 

import chromadb from sentence_transformers import SentenceTransformer 

model = SentenceTransformer("all-MiniLM-L6-v2") client = chromadb.Client() collection = client.create_collection("day6_intro") 

documents = [ "The cat sat on the mat.", "She is learning to code in Python.", "The restaurant had no tables available.", "He is studying machine learning.", "A feline rested on the rug.", "The diner was fully booked.", ] 

embeddings = model.encode(documents).tolist() ids = [f"doc_{i}" for i in range(len(documents))] 

collection.add(documents=documents, embeddings=embeddings, ids=ids) 

query = "programming and AI" query_embedding = model.encode([query]).tolist() 

results = collection.query(query_embeddings=query_embedding, n_results=3) 

print(f"Query: '{query}'\n") 

for doc, distance in zip(results["documents"][0], results["distances"][0]): print(f"  {1 - distance:.3f}  {doc}") 

Note: Chroma returns distances (lower = more similar), not similarity scores. Subtract from 1 to convert to a similarity score you can read intuitively. 

Did the right documents come back? Try changing the query to "cats and animals" and see what changes. 

## **2. Persistent Storage** 

## **In-memory vs on-disk** 

chromadb.Client() keeps everything in memory — fast, but gone when your script exits. For anything real, use a persistent client that saves to disk: 

client = chromadb.PersistentClient(path="./chroma_db") 

Everything is saved to the ./chroma_db folder automatically. The next time your script runs, it loads from disk — no re-embedding needed. 

## **Getting or creating a collection** 

When using persistent storage, use get_or_create_collection instead of create_collection . If the collection already exists it loads it; if not, it creates it. 

collection = client.get_or_create_collection("my_collection") 

## **Exercises — Persistent Storage** 

## **Exercise 2 — Persist a collection across runs** 

Run this script twice. The first run embeds and stores the documents. The second run loads them from disk and queries — no embedding step needed. 

import chromadb 

from sentence_transformers import SentenceTransformer 

client = chromadb.PersistentClient(path="./chroma_db") 

collection = client.get_or_create_collection("persistent_demo") 

# Only add documents if the collection is empty 

if collection.count() == 0: 

print("First run — embedding and storing documents...") model = SentenceTransformer("all-MiniLM-L6-v2") 

documents = [ 

"Python is a high-level programming language.", 

"Machine learning models learn from data.", 

"Karachi is the largest city in Pakistan.", 

"The Gemini API provides access to large language models.", 

"Embeddings represent text as vectors of numbers.", 

"Islamabad is the capital of Pakistan.", 

"Neural networks are inspired by the human brain.", 

"Lahore is known for its rich cultural heritage.", 

] 

embeddings = model.encode(documents).tolist() 

ids = [f"doc_{i}" for i in range(len(documents))] collection.add(documents=documents, embeddings=embeddings, ids=ids) print(f"Stored {len(documents)} documents.\n") else: 

print(f"Loaded existing collection with {collection.count()} documents.\n") model = SentenceTransformer("all-MiniLM-L6-v2") 

query = "cities in Pakistan" results = collection.query( query_embeddings=model.encode([query]).tolist(), n_results=3, 

) 

print(f"Query: '{query}'\n") for doc, distance in zip(results["documents"][0], results["distances"][0]): print(f"  {1 - distance:.3f}  {doc}") 

After the first run, open the ./chroma_db folder — you'll see files there. On the second run, the embedding step is skipped entirely. 

## **Exercise 3 — Load 50 documents and search them** 

Generate a larger set of documents, store them all, and run several different queries to see how the results change. 

import chromadb 

from sentence_transformers import SentenceTransformer 

model = SentenceTransformer("all-MiniLM-L6-v2") client = chromadb.Client() collection = client.create_collection("fifty_docs") 

documents = [ # Technology "Python is widely used for data science and machine learning.", "JavaScript is the primary language of web development.", "Rust is known for memory safety and performance.", "Docker containers make software deployment consistent.", "Git is the standard tool for version control.", "APIs allow different software systems to communicate.", "Cloud computing provides on-demand computing resources.", "Open source software is freely available to modify and share.", "Databases store and organise structured data.", "Machine learning models improve with more training data.", # Science "The speed of light is approximately 300,000 km per second.", "DNA carries genetic information in living organisms.", "Photosynthesis converts sunlight into energy for plants.", "Black holes have gravitational pull so strong light cannot escape.", "The periodic table organises all known chemical elements.", "Quantum mechanics describes physics at the subatomic level.", "Climate change is driven largely by greenhouse gas emissions.", "The human brain contains roughly 86 billion neurons.", "Vaccines train the immune system to fight specific diseases.", "Evolution occurs through natural selection over generations.", # History "The Second World War ended in 1945.", "Pakistan gained independence on 14 August 1947.", "The invention of the printing press changed the spread of knowledge.", "The Industrial Revolution transformed manufacturing in the 18th century.", "The moon landing took place in July 1969.", "The Roman Empire lasted for over a thousand years.", "The Silk Road was an ancient trade route connecting East and West.", "The French Revolution began in 1789.", "Genghis Khan founded the Mongol Empire in the 13th century.", "The Berlin Wall fell in 1989.", # Health "Regular exercise reduces the risk of cardiovascular disease.", "Sleep deprivation impairs memory and cognitive function.", "A balanced diet includes proteins, carbohydrates, and healthy fats.", "Stress can have significant negative effects on physical health.", "Drinking enough water is essential for bodily functions.", "Mental health is as important as physical health.", "Smoking is a leading cause of preventable death worldwide.", 

"Meditation has been shown to reduce anxiety and improve focus.", "Vitamin D deficiency is common in regions with low sunlight.", "Hand washing is one of the most effective ways to prevent illness.", # Business 

"A startup is a young company trying to solve a problem at scale.", "Cash flow is often more important than profit for small businesses.", "Marketing involves understanding and reaching your target audience.", "Supply chain disruptions can affect product availability globally.", "Remote work has become common since the COVID-19 pandemic.", "Venture capital funds early-stage companies in exchange for equity.", "Customer retention is cheaper than acquiring new customers.", "A business model describes how a company creates and captures value.", "Data-driven decisions tend to outperform decisions based on intuition.", "Branding is how a company presents itself to the world.", 

] 

embeddings = model.encode(documents).tolist() ids = [f"doc_{i}" for i in range(len(documents))] collection.add(documents=documents, embeddings=embeddings, ids=ids) 

print(f"Stored {collection.count()} documents.\n") 

queries = [ "programming languages", "human body and health", "ancient history", "running a company", "space and physics", ] 

for query in queries: results = collection.query( query_embeddings=model.encode([query]).tolist(), n_results=3, ) print(f"Query: '{query}'") for doc, distance in zip(results["documents"][0], results["distances"][0]): print(f"  {1 - distance:.3f}  {doc}") print() 

Look at each set of results. Are the top matches actually relevant? Are there any surprises — relevant documents that you wouldn't have found with keyword search? 

## **3. Metadata and Filtering** 

## **Why metadata matters** 

Every document you add to Chroma can carry **metadata** — a dictionary of extra information about that document. You can then filter your queries so they only search within a subset of the collection. 

This is important for real applications. Imagine a knowledge base with documents from multiple departments. A user in the HR department should only search HR documents, not engineering docs. 

## **Adding metadata** 

collection.add( 

documents=["The refund takes 5 to 7 days.", "Deploy using Docker Compose."], 

embeddings=[...], 

ids=["hr_001", "eng_001"], 

metadatas=[{"department": "hr"}, {"department": "engineering"}], 

) 

## **Filtering queries** 

results = collection.query( 

query_embeddings=[...], n_results=2, where={"department": "hr"},   # only search HR documents 

) 

## **Exercises — Metadata and Filtering** 

## **Exercise 4 — Add metadata and filter by category** 

import chromadb from sentence_transformers import SentenceTransformer 

model = SentenceTransformer("all-MiniLM-L6-v2") client = chromadb.Client() 

collection = client.create_collection("with_metadata") 

documents = [ 

("Python is used for machine learning.", "tech"), 

("Docker simplifies deployment.", "tech"), 

("Regular exercise improves heart health.", "health"), 

("Sleep is essential for brain function.", "health"), 

("A startup needs a clear business model.", "business"), 

("Customer retention is key to growth.", "business"), 

("Git tracks changes in your codebase.", "tech"), 

("A balanced diet supports immune function.", "health"), 

] 

texts     = [d[0] for d in documents] metadatas = [{"category": d[1]} for d in documents] embeddings = model.encode(texts).tolist() ids = [f"doc_{i}" for i in range(len(texts))] 

collection.add( documents=texts, embeddings=embeddings, ids=ids, metadatas=metadatas, ) 

query = "staying healthy" query_embedding = model.encode([query]).tolist() 

print(f"Query: '{query}'\n") 

print("Without filter (all categories):") results = collection.query(query_embeddings=query_embedding, n_results=3) for doc, dist in zip(results["documents"][0], results["distances"][0]): print(f"  {1 - dist:.3f}  {doc}") 

print("\nWith filter (health only):") results = collection.query( query_embeddings=query_embedding, n_results=3, where={"category": "health"}, ) for doc, dist in zip(results["documents"][0], results["distances"][0]): print(f"  {1 - dist:.3f}  {doc}") 

Does filtering change which documents come back? Try the same query filtered to "tech" — what happens? 

## **Exercise 5 — Inspect what's in your collection** 

Chroma lets you peek inside a collection — useful for debugging when results don't look right. 

import chromadb from sentence_transformers import SentenceTransformer 

model = SentenceTransformer("all-MiniLM-L6-v2") client = chromadb.Client() collection = client.create_collection("inspection_demo") 

documents = [ 

("Machine learning is a subfield of AI.", {"topic": "ai", "level": "intro"}), 

("Gradient descent optimises neural networks.", {"topic": "ai", "level": "advanced"}), 

("Karachi has a population of over 14 million.", {"topic": "geography", "level": "intro"}), 

("The Indus Valley Civilisation is one of the oldest.", {"topic": "history", "level": "intro"}), ("Transformers use self-attention mechanisms.", {"topic": "ai", "level": "advanced"}), ] 

texts     = [d[0] for d in documents] metadatas = [d[1] for d in documents] embeddings = model.encode(texts).tolist() ids = [f"doc_{i}" for i in range(len(texts))] 

collection.add(documents=texts, embeddings=embeddings, ids=ids, metadatas=metadatas) 

# How many documents? print(f"Total documents: {collection.count()}\n") 

# Peek at the first 3 peek = collection.peek(limit=3) print("First 3 documents:") for doc_id, doc, meta in zip(peek["ids"], peek["documents"], peek["metadatas"]): print(f"  [{doc_id}] {meta}  |  {doc}") 

print() 

# Query with two filters print("Advanced AI documents only:") results = collection.query( query_embeddings=model.encode(["how do neural networks learn"]).tolist(), n_results=5, where={"$and": [{"topic": "ai"}, {"level": "advanced"}]}, ) for doc in results["documents"][0]: print(f"  {doc}") 

Try changing the where filter — search for intro-level AI docs, or all geography docs. Notice how $and lets you combine multiple conditions. 

## **Check Your Understanding** 

Before moving to Day 7, make sure you can answer these without looking: 

1. What problem does a vector database solve that a plain NumPy array doesn't? 

2. What is the difference between chromadb.Client() and 

   - chromadb.PersistentClient() ? 

3. Why use get_or_create_collection instead of create_collection in a persistent setup? 

4. Chroma returns distances , not similarity scores. If a distance is 0.1, is that a good or bad match? 

5. You're building a Q&A bot for a company with three departments. How would you use metadata to make sure each department only searches their own documents? 

