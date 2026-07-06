## **Day 5 — Embeddings** 

One of the most powerful ideas in modern AI — and simpler than it sounds. 

## **1. What an Embedding Is and Why It Works** 

## **The core idea** 

An embedding is a way of turning text into a list of numbers — a **vector** — such that text with similar _meaning_ gets similar numbers. 

That's it. But the implication is enormous: once text is a vector, you can do maths on meaning. 

For example: 

- "I love dogs" → [0.21, -0.54, 0.88, ...] (hundreds of numbers) 

- "I adore puppies" → [0.23, -0.51, 0.85, ...] (very similar numbers) 

- "The stock market crashed" → [-0.61, 0.34, -0.12, ...] (very different numbers) 

A traditional keyword search can't tell that "dogs" and "puppies" are related — they're different strings. An embedding search can, because both sentences land close together in vector space. 

## **Why it works** 

Embedding models are trained on enormous amounts of text. Through that training they learn that words and phrases that appear in similar contexts carry similar meanings. The numbers in the vector encode that learned context. Two sentences that mean the same thing will have been seen in similar contexts during training, so their vectors end up pointing in roughly the same direction. 

You don't need to understand the internals to use this effectively — just the intuition: **similar meaning → similar vector** . 

## **Exercise — See embeddings with your own eyes** 

**Exercise 1 — Generate your first embeddings** 

Install Sentence Transformers, a free library that runs embedding models locally with no API key: 

pip install sentence-transformers 

Then run this script. It prints the first 8 numbers of each embedding so you can see the vectors are different for different sentences. 

from sentence_transformers import SentenceTransformer 

model = SentenceTransformer("all-MiniLM-L6-v2") 

sentences = [ "I love dogs.", "I adore puppies.", "The stock market crashed today.", "Python is a programming language.", "She has a pet cat.", 

] 

embeddings = model.encode(sentences) 

for sentence, vector in zip(sentences, embeddings): preview = ", ".join(f"{x:.3f}" for x in vector[:8]) print(f"{sentence}") print(f"  [{preview}, ...]  ({len(vector)} dimensions total)") print() 

Notice the shape of the numbers. Do the dog-related sentences look more similar to each other than to the stock market sentence? 

## **2. Cosine Similarity — Intuition** 

## **What it measures** 

Once you have two vectors, you need a way to measure how similar they are. The standard method is **cosine similarity** . 

Think of each vector as an arrow pointing from the origin in multi-dimensional space. Cosine similarity measures the _angle_ between two arrows: 

- **Score = 1.0** — arrows point in exactly the same direction → identical meaning 

- **Score = 0.0** — arrows are perpendicular → unrelated 

- **Score = -1.0** — arrows point in opposite directions → opposite meaning 

In practice, sentence embeddings almost never go negative. You'll mostly see scores between 0.3 (loosely related) and 0.99 (nearly identical). 

You don't need to know the formula. What matters is: **higher score = more similar meaning** . 

## **Exercises — Cosine Similarity** 

## **Exercise 2 — Compute similarity between sentence pairs** 

from sentence_transformers import SentenceTransformer from sklearn.metrics.pairwise import cosine_similarity 

## model = SentenceTransformer("all-MiniLM-L6-v2") 

pairs = [ ("I love dogs.", "I adore puppies."), 

("I love dogs.", "The stock market crashed."), 

("Python is a programming language.", "I use Python to write code."), 

("Python is a programming language.", "The snake slithered through the grass."), 

("She is happy.", "She is sad."), 

] 

for a, b in pairs: vec_a = model.encode([a]) vec_b = model.encode([b]) score = cosine_similarity(vec_a, vec_b)[0][0] print(f"{score:.3f}  |  '{a}'  vs  '{b}'") 

Install sklearn if needed: 

pip install scikit-learn 

Look at the scores. Does "Python the language" vs "Python the snake" get a lower score than "Python the language" vs "I use Python to write code"? What does that tell you? 

**Exercise 3 — Find the odd one out** 

Embed a list of sentences and find the one that's most different from the rest. 

from sentence_transformers import SentenceTransformer from sklearn.metrics.pairwise import cosine_similarity import numpy as np 

model = SentenceTransformer("all-MiniLM-L6-v2") 

sentences = [ "I enjoy hiking in the mountains.", "Trail running is my favourite weekend activity.", "The neural network has three hidden layers.", "Camping under the stars is deeply relaxing.", "She loves outdoor adventures.", ] 

embeddings = model.encode(sentences) similarity_matrix = cosine_similarity(embeddings) 

# Average similarity of each sentence to all others avg_similarities = similarity_matrix.mean(axis=1) 

odd_one_out = sentences[np.argmin(avg_similarities)] print("Odd one out:", odd_one_out) print() for sentence, score in zip(sentences, avg_similarities): print(f"{score:.3f}  {sentence}") 

Did it find the right outlier? Try swapping in your own sentences and see if the result still makes sense. 

## **3. Local Embeddings with Sentence Transformers** 

## **Why local embeddings** 

Sentence Transformers runs entirely on your machine — no API key, no quota, no cost per call, and nothing sent over the internet. For learning and for any application handling private data, this is ideal. 

The model all-MiniLM-L6-v2 is a good default: fast, small (~80 MB), and good enough for most tasks. It produces 384-dimensional vectors. 

## **The two things you'll always do** 

from sentence_transformers import SentenceTransformer 

# 1. Load the model once (downloads on first run, cached after) model = SentenceTransformer("all-MiniLM-L6-v2") 

# 2. Encode text — pass a string or a list of strings single  = model.encode("one sentence")           # returns a 1D array batch   = model.encode(["sentence one", "two"])  # returns a 2D array 

Always encode in batches when you have multiple strings — it's significantly faster than a loop. 

## **Exercise — Batch encoding** 

## **Exercise 4 — Encode a batch and time it** 

Compare encoding sentences one at a time in a loop versus encoding them all at once in a batch. 

import time 

from sentence_transformers import SentenceTransformer 

model = SentenceTransformer("all-MiniLM-L6-v2") 

sentences = [f"This is sentence number {i}." for i in range(100)] 

# One at a time start = time.time() for s in sentences: model.encode(s) loop_time = round(time.time() - start, 3) 

# All at once start = time.time() model.encode(sentences) batch_time = round(time.time() - start, 3) 

print(f"Loop:  {loop_time}s") print(f"Batch: {batch_time}s") print(f"Batch is {round(loop_time / batch_time)}x faster") 

How large is the speedup? For a real application processing thousands of documents, this difference is significant. 

## **4. Comparing Meaning, Not Keywords** 

## **Why this matters** 

Traditional search matches keywords. If you search for "car" and a document says "automobile", you miss it. Embedding-based search finds it — because "car" and "automobile" land close together in vector space. 

This is the foundation of everything in Week 3 (RAG — Retrieval Augmented Generation). Before you can build a document Q&A system, you need to understand how semantic search works. 

The pattern is always the same: 

1. Embed all your documents (do this once, store the results) 

2. Embed the user's query 

3. Find the documents whose vectors are closest to the query vector 

4. Return those documents as results 

## **Exercises — Semantic Search** 

## **Exercise 5 — Keyword search vs semantic search** 

Write both a keyword search and a semantic search over the same set of sentences, then compare the results on the same queries. 

from sentence_transformers import SentenceTransformer from sklearn.metrics.pairwise import cosine_similarity import numpy as np 

model = SentenceTransformer("all-MiniLM-L6-v2") 

documents = [ 

- "The car broke down on the highway.", 

- "She adopted a puppy from the shelter.", 

- "The automobile engine needs replacing.", 

- "He is learning to play the guitar.", 

- "The dog was found wandering near the park.", 

"Electric vehicles are becoming more affordable.", "She practises piano every evening.", 

] 

doc_embeddings = model.encode(documents) 

def keyword_search(query, docs): query_lower = query.lower() return [d for d in docs if any(word in d.lower() for word in query_lower.split())] 

def semantic_search(query, docs, doc_embeds, top_k=3): query_embed = model.encode([query]) scores = cosine_similarity(query_embed, doc_embeds)[0] top_indices = np.argsort(scores)[::-1][:top_k] return [(docs[i], round(scores[i], 3)) for i in top_indices] 

queries = [ "vehicle problems", "pets", "music", ] 

for query in queries: print(f"Query: '{query}'") print(f"  Keyword results: {keyword_search(query, documents) or 'none'}") print(f"  Semantic results:") for doc, score in semantic_search(query, documents, doc_embeddings): print(f"    {score:.3f}  {doc}") print() 

Where does keyword search fail? Where does semantic search succeed? Note the cases where semantic search finds relevant documents that don't share a single word with the query. 

## **Exercise 6 — Find the three closest pairs** 

Embed 20 sentences and find which three pairs are most similar to each other — without any prior knowledge of what the sentences say. 

from sentence_transformers import SentenceTransformer from sklearn.metrics.pairwise import cosine_similarity import numpy as np 

model = SentenceTransformer("all-MiniLM-L6-v2") 

sentences = [ "The cat sat on the mat.", "A feline rested on the rug.", "She is learning to code in Python.", "He is studying programming with Python.", "The restaurant was fully booked.", "There were no tables available at the diner.", "Climate change is accelerating.", "Global warming is getting worse.", "He went for a run in the park.", "She jogged through the garden.", "The flight was delayed by two hours.", "The plane departed late.", "Inflation is rising across the country.", "Prices are going up everywhere.", "The movie was boring and too long.", "The film dragged on and was dull.", "She plays football on weekends.", "He enjoys a game of soccer on Saturdays.", "The hospital was understaffed.", "There were not enough doctors on duty.", ] embeddings = model.encode(sentences) similarity_matrix = cosine_similarity(embeddings) 

# Zero out the diagonal (self-similarity = 1.0, not useful) np.fill_diagonal(similarity_matrix, 0) 

# Find the top 3 pairs pairs = [] for i in range(len(sentences)): for j in range(i + 1, len(sentences)): pairs.append((similarity_matrix[i][j], i, j)) 

pairs.sort(reverse=True) 

print("Top 3 most similar pairs:\n") for score, i, j in pairs[:3]: print(f"Score: {score:.3f}") print(f"  A: {sentences[i]}") print(f"  B: {sentences[j]}") 

print() 

Did the model correctly identify the most similar pairs? Look at the scores — are paraphrases scoring close to 1.0? Are unrelated sentences scoring close to 0? 

## **Check Your Understanding** 

Before moving to Day 6, make sure you can answer these without looking: 

1. What does an embedding actually represent — what are those hundreds of numbers? 

2. Two sentences score 0.95 cosine similarity. What does that tell you about their meaning? 

3. Why would a keyword search for "vehicle issues" miss a document that says "the car broke down"? Why would a semantic search find it? 

4. Why is it faster to call model.encode(list_of_sentences) once rather than calling model.encode(sentence) in a loop? 

5. You're building a support bot. A user types "my screen is cracked". Your knowledge base contains "display replacement procedure". Would semantic search find it? Would keyword search? 

