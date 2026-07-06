## **Day 9 — Your First Web UI with Streamlit** 

Your RAG pipeline works in the terminal. Today you give it a proper interface anyone can use in a browser — with no front-end experience needed. 

**What you're bringing in:** the full RAG pipeline with overlapping chunks and citations (Days 7–8). Today you wrap it in a UI, not rebuild it. 

## **1. Streamlit Basics** 

## **What Streamlit is** 

Streamlit is a Python library that turns a Python script into a web app. You write pure Python — no HTML, no CSS, no JavaScript. Streamlit handles the browser rendering. 

This makes it the right tool for AI engineers who want to demo or ship something quickly without becoming a front-end developer. 

Install it: 

pip install streamlit 

Run any Streamlit script: 

streamlit run app.py 

This opens a browser tab at http://localhost:8501 automatically. 

## **The key mental model** 

A Streamlit script runs **top to bottom, every time something changes** on the page — a button click, a text input, a file upload. Think of it as the page re-rendering from scratch on each interaction. This means you need to be careful about expensive operations (like embedding a document) — you don't want to re-run them on every interaction. Streamlit's @st.cache_resource decorator fixes this. 

## **The core building blocks** 

import streamlit as st st.title("My App")                        # large heading st.write("Some text or a value")          # flexible output st.text_input("Label")                    # text box, returns the string typed st.button("Click me")                     # returns True when clicked st.file_uploader("Upload", type=["txt"])  # returns a file object or None st.spinner("Loading...")                  # shows a loading indicator st.success("Done!")                       # green success box st.error("Something went wrong.")         # red error box st.markdown("**bold** and _italic_")      # markdown rendering 

## **Exercises — Streamlit Basics** 

**Exercise 1 — Your first Streamlit page** 

Create a file called hello.py and run it with streamlit run hello.py . 

import streamlit as st 

st.title("Hello, Streamlit") st.write("This is my first web app.") 

name = st.text_input("What is your name?") 

if name: 

st.success(f"Nice to meet you, {name}!") 

Open the browser tab. Type your name in the box. Notice how the page updates immediately without a page reload. Change the st.success to st.error and save — Streamlit hot-reloads the app automatically. 

## **Exercise 2 — Understand re-renders** 

This exercise makes the re-render behaviour visible. 

import streamlit as st import time 

st.title("Re-render Demo") 

st.write(f"Page rendered at: {time.strftime('%H:%M:%S')}") 

user_input = st.text_input("Type anything:") 

if user_input: 

st.write(f"You typed: {user_input}") 

if st.button("Click me"): st.write("Button was clicked.") 

Run it. Type in the box, click the button, observe the timestamp. Every interaction causes the whole script to re-run — notice the timestamp updates each time. This is the behaviour you need to understand before building anything stateful. 

## **Exercise 3 — File upload** 

import streamlit as st 

st.title("File Upload Demo") 

uploaded_file = st.file_uploader("Upload a text file", type=["txt"]) 

if uploaded_file is not None: 

content = uploaded_file.read().decode("utf-8") 

st.success(f"File uploaded: {uploaded_file.name} ({len(content)} characters)") st.text_area("File contents", content, height=300) 

else: 

st.info("Upload a .txt file to see its contents.") 

Create a small .txt file on your computer and upload it. Observe that uploaded_file is None when no file is present — your code always needs to check for this before trying to read it. 

## **2. Caching Expensive Operations** 

## **The problem** 

Your RAG pipeline loads a model (~80 MB), embeds documents, and builds a Chroma collection. If Streamlit re-runs the script on every interaction, all of that happens again on every keypress — making the app unusably slow. 

## **The solution: @st.cache_resource** 

Use @st.cache_resource for objects that are expensive to create and should be shared across re-renders: models, database connections, and indexed collections. 

@st.cache_resource def load_embed_model(): from sentence_transformers import SentenceTransformer return SentenceTransformer("all-MiniLM-L6-v2") 

The first call runs the function and caches the result. Every subsequent call returns the cached object instantly — regardless of how many times the page re-renders. 

**Exercise — See caching in action** 

## **Exercise 4 — With and without caching** 

import streamlit as st import time from sentence_transformers import SentenceTransformer 

st.title("Caching Demo") 

# Toggle this decorator on and off to feel the difference @st.cache_resource def load_model(): time.sleep(2)  # simulate a slow load return SentenceTransformer("all-MiniLM-L6-v2") 

st.write("Loading model...") model = load_model() st.success("Model ready.") text = st.text_input("Enter text to embed:") if text: embedding = model.encode(text) st.write(f"Embedding shape: {embedding.shape}") st.write(f"First 5 values: {embedding[:5].tolist()}") 

Run it the first time — the 2-second delay is visible. Type in the text box and notice the model loads instantly on subsequent re-renders. Now remove @st.cache_resource and try again — the 2-second delay happens on every keypress. 

## **3. Building the RAG App** 

Now wrap your Day 7–8 RAG pipeline inside a Streamlit interface. Build it step by step — get each piece working in the browser before adding the next. 

## **Exercise — Step by step build** 

**Exercise 5 — Upload, index, ask, cite** 

Create rag_app.py . Build it in these stages, running streamlit run rag_app.py after each one to verify it works in the browser. 

**Stage A — Page structure and file upload** 

import streamlit as st st.title("Document Q&A") st.write("Upload a text file and ask questions about it.") 

uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"]) 

if uploaded_file: st.success(f"Uploaded: {uploaded_file.name}") else: st.info("Upload a document to get started.") 

Run it. Upload a file. Confirm the success message appears. 

**Stage B — Add chunking and indexing** 

import streamlit as st import chromadb from sentence_transformers import SentenceTransformer 

@st.cache_resource def load_embed_model(): return SentenceTransformer("all-MiniLM-L6-v2") def overlapping_chunks(text, n=3, overlap=1): sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()] step = n - overlap chunks = [] for i in range(0, len(sentences), step): group = sentences[i:i + n] if group: chunks.append(". ".join(group) + ".") return chunks def build_collection(text, embed_model): chunks = overlapping_chunks(text) client = chromadb.Client() collection = client.create_collection("rag_collection") embeddings = embed_model.encode(chunks).tolist() ids = [f"c_{i}" for i in range(len(chunks))] collection.add(documents=chunks, embeddings=embeddings, ids=ids) return collection, len(chunks) 

embed_model = load_embed_model() 

st.title("Document Q&A") 

uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"]) 

if uploaded_file: text = uploaded_file.read().decode("utf-8") with st.spinner("Indexing document..."): collection, chunk_count = build_collection(text, embed_model) st.success(f"Indexed {chunk_count} chunks from {uploaded_file.name}") else: st.info("Upload a document to get started.") 

Upload a file. Confirm the chunk count appears. Note the spinner while indexing runs. 

## **Stage C — Add the question input and RAG answer** 

import os import streamlit as st import chromadb import google.generativeai as genai from sentence_transformers import SentenceTransformer from dotenv import load_dotenv 

load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) @st.cache_resource def load_embed_model(): return SentenceTransformer("all-MiniLM-L6-v2") @st.cache_resource def load_llm(): return genai.GenerativeModel( model_name="gemini-1.5-flash", system instruction=( 

system_instruction=( 

"Answer using only the context provided. " 

"If the answer is not in the context, say 'I don't have that information.'" ), ) 

def overlapping_chunks(text, n=3, overlap=1): sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()] step = n - overlap chunks = [] for i in range(0, len(sentences), step): group = sentences[i:i + n] if group: chunks.append(". ".join(group) + ".") return chunks 

def build_collection(text, embed_model): chunks = overlapping_chunks(text) client = chromadb.Client() collection = client.create_collection("rag_collection") embeddings = embed_model.encode(chunks).tolist() ids = [f"c_{i}" for i in range(len(chunks))] collection.add(documents=chunks, embeddings=embeddings, ids=ids) return collection, len(chunks) 

def ask(question, collection, embed_model, llm): results = collection.query( 

query_embeddings=embed_model.encode([question]).tolist(), n_results=3, ) used_chunks = results["documents"][0] context = "\n\n".join(f"- {c}" for c in used_chunks) prompt = f"Context:\n{context}\n\nQuestion: {question}" answer = llm.generate_content(prompt).text.strip() return answer, used_chunks 

# ── UI ──────────────────────────────────────────────────────────── 

embed_model = load_embed_model() llm = load_llm() 

st.title("Document Q&A") 

uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"]) 

if uploaded_file: 

text = uploaded_file.read().decode("utf-8") 

with st.spinner("Indexing document..."): collection, chunk_count = build_collection(text, embed_model) 

st.success(f"Indexed {chunk_count} chunks from {uploaded_file.name}") 

question = st.text_input("Ask a question about the document:") 

if question: 

with st.spinner("Thinking..."): answer, sources = ask(question, collection, embed_model, llm) 

st.markdown("### Answer") st.write(answer) 

st.markdown("### Sources") for i, source in enumerate(sources, 1): st.markdown(f"**[{i}]** {source}") 

else: 

st.info("Upload a document to get started.") 

This is your complete app. Upload a .txt file, type a question, and see the answer with citations rendered in the browser. 

Test it with: 

A question clearly answered in the document 

A question not in the document — does it say so? 

An empty question (just hit Enter) — does anything break? 

## **4. Polish and Edge Cases** 

A working app and a good app are different things. These small additions matter. 

## **Exercise — Handle the obvious edge cases** 

**Exercise 6 — Make the app robust** 

Add these improvements to your rag_app.py : 

## **A — Show a document preview** 

After a file is uploaded, show the first 500 characters so the user knows what was loaded: 

with st.expander("Document preview"): st.text(text[:500] + "..." if len(text) > 500 else text) 

## **B — Warn on very short documents** 

If the document produces fewer than 3 chunks it's probably too short to be useful: 

if chunk_count < 3: 

st.warning("This document is very short. Results may be limited.") 

**C — Handle indexing errors gracefully** 

Wrap the build_collection call: 

try: 

with st.spinner("Indexing document..."): 

collection, chunk_count = build_collection(text, embed_model) 

st.success(f"Indexed {chunk_count} chunks.") except Exception as e: st.error(f"Failed to index document: {e}") st.stop() 

st.stop() halts the rest of the script from running — useful when a critical step fails and proceeding would cause more confusing errors. 

**D — Disable the input until a document is loaded** 

question = st.text_input( 

"Ask a question about the document:", disabled=uploaded_file is None, placeholder="Upload a document first..." if uploaded_file is None else "Type your question...", ) 

Add all four improvements and test each one. Upload a very short document to trigger the warning. Temporarily break your API key to trigger the error handler. 

## **Check Your Understanding** 

Before moving to Day 10, make sure you can answer these without looking: 

1. Why does a Streamlit script re-run from top to bottom on every interaction? 

2. What is @st.cache_resource for, and what goes wrong without it? 3. uploaded_file is None when no file has been uploaded. Why do you always need to check for this before reading the file? 

4. What does st.stop() do and when is it useful? 5. Your app re-indexes the document every time the user types a character in the question box. What is causing this and how would you fix it? 

