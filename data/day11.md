## **Day 11 — Build a Small Agent** 

Yesterday you hand-wrote the ReAct loop. Today you extend it into something real — multiple tools, model-driven tool choice, a runaway loop guard, and a complete Document Q&A web app. 

**What you're bringing in:** the full ReAct loop from Day 10, the RAG pipeline from Days 7–8, and the Streamlit UI from Day 9. The second half of today brings all three together into your second portfolio project. 

## **1. Defining Two or Three Tools** 

## **From one tool to many** 

On Day 10 you had two tools: calculator and a fake search with hardcoded responses. A real agent needs tools that return real data. Today you'll add a third tool and wire in a real web search option. 

The pattern for adding a new tool is always the same: 

1. Write the Python function 

2. Add it to the TOOLS dict 

3. Add a description to the system prompt 

4. Test it in isolation before plugging it into the agent 

## **Tool design principles** 

**Return strings.** Your agent loop appends tool output to the conversation as text. Always return a string from a tool — even if the underlying data is a number or a dict, convert it before returning. 

**Return something useful on failure.** Never let a tool raise an exception into the loop. Catch errors inside the function and return a descriptive error string so the model can reason about what went wrong and try something else. 

**Keep tools focused.** A tool that does one thing is easier for the model to use correctly than a tool that does several. If you find yourself writing an if/elif inside a tool based on what the user wants, split it into two tools. 

## **Exercise 1 — Add a unit converter tool** 

Write a third tool called convert(expression) that handles common unit conversions. It should support at minimum: km to miles, miles to km, kg to lbs, lbs to kg, Celsius to Fahrenheit, and Fahrenheit to Celsius. 

The input will be a string like "5 km to miles" or "100 celsius to fahrenheit" . 

Parse the expression, do the conversion, and return a formatted string. Return a helpful error message if the expression isn't recognised. 

Test it directly on these inputs before connecting it to the agent: 

**Expected output:** 

5 km = 3.107 miles 100 Celsius = 212.0 Fahrenheit 70 kg = 154.324 lbs No conversion found for: 10 parsecs to lightyears 

## **Exercise 2 — Update your system prompt** 

Add the convert tool to your system prompt with a clear description and an example input. The description should make it obvious when the model should use convert versus calculator . 

Print your updated system prompt and check that the three tools are described consistently — same format, same level of detail. 

**Expected output:** 

You are an agent that can use tools to answer questions. 

You have access to these tools: 

- calculator: Evaluates a mathematical expression. Use for any arithmetic. Input: a mathematical expression, e.g. "17 * 38" or "sqrt(144)" 

- search: Searches for factual information. 

Input: a short search query, e.g. "population of Pakistan" 

- convert: Converts between common units. Input: a conversion expression, e.g. "5 km to miles" or "100 celsius to fahrenheit" 

To use a tool: Thought: <your reasoning> Action: <tool name> Input: <tool input> 

When you have a final answer: Thought: <your reasoning> Final Answer: <your answer> 

Always use tools for calculations, facts, and conversions. Never guess at numbers. 

## **2. Letting the Model Choose Which Tool to Use** 

## **Why this matters** 

On Day 10 every question required you to know which tool the model would need. In a real agent, you don't know in advance — the model reads the question, reasons about what it needs, and picks the appropriate tool. 

The only thing that guides this choice is your system prompt. If the tool descriptions are clear and distinct, the model will generally pick correctly. If they're vague or overlap, it will guess — sometimes wrong. 

## **Exercise 3 — Test tool selection** 

Run your three-tool agent on this set of questions without telling the model which tool to use. Observe which tool it picks for each one. 

## Questions to test: 

- "How many miles is 42 kilometres?" 

- "What is the square root of 2025?" 

- "What is the capital of France?" 

- "Convert 37 degrees Celsius to Fahrenheit." 

- "What is the population of Pakistan divided by the area of Pakistan?" 

## **Expected output (first question):** 

Question: How many miles is 42 kilometres? 

--- Step 1 --Thought: The user wants to convert kilometres to miles. I'll use the convert tool. Action: convert Input: 42 km to miles 

[Tool: convert('42 km to miles')] [Observation: 42 km = 26.098 miles] 

--- Step 2 --Thought: I have the answer. Final Answer: 42 kilometres is approximately 26.1 miles. 

For the last question (population divided by area), count how many tool calls the model makes and in what order. Did it search for both values before calculating? 

## **Exercise 4 — Observe wrong tool selection** 

Deliberately give the agent a question where it might pick the wrong tool. 

Run: "What is 5 kilometres times the speed of light?" 

This requires both convert (or calculator ) and search . Watch whether the model recognises it needs to search for the speed of light first, or whether it tries to calculate with a unit it doesn't have. 

**Expected output (correct path):** 

Question: What is 5 kilometres times the speed of light? 

--- Step 1 --Thought: I need the speed of light first. Action: search Input: speed of light 

[Tool: search('speed of light')] [Observation: The speed of light is approximately 299,792 km per second.] 

--- Step 2 --Thought: Now I can multiply 5 km by 299,792 km/s. Action: calculator Input: 5 * 299792 

[Tool: calculator('5 * 299792')] [Observation: 1498960] 

--- Step 3 --Thought: I have the answer. Final Answer: 5 kilometres times the speed of light is 1,498,960 km²/s. 

If the model takes a wrong path, note exactly where it diverged. Was it the first tool choice, the input format, or the reasoning between steps? 

## **3. Real Web Search** 

## **The problem with hardcoded responses** 

Your search tool currently returns from a fixed dictionary. This is fine for testing the loop, but it means your agent can only answer questions you anticipated. A real agent needs real search. 

## **Free options** 

**DuckDuckGo Instant Answer API** — free, no key required, returns JSON. Limited to DuckDuckGo's instant answer data (good for facts, not for full web results). 

https://api.duckduckgo.com/?q=population+of+Pakistan&format=json&no_html=1 

**Serper API** — 2,500 free searches per month with a free account at serper.dev. Returns Google search results as JSON. 

**Wikipedia API** — completely free, no key, returns article summaries in JSON. Excellent for factual questions. 

https://en.wikipedia.org/api/rest_v1/page/summary/Pakistan 

The Wikipedia API is the right choice for this course — no sign-up, no quota, reliable results. 

## **Exercise 5 — Replace the fake search with Wikipedia** 

Rewrite your search tool to call the Wikipedia summary API instead of returning from a hardcoded dict. 

The endpoint is: https://en.wikipedia.org/api/rest_v1/page/summary/{topic} 

Replace spaces in the query with underscores. Parse the JSON response and return the extract field — that's the plain-text summary. If the request fails or the page doesn't exist, return a helpful error string. 

Install requests if you haven't already: pip install requests 

Test your new search tool directly on a few topics before connecting it to the agent: 

**Expected output:** 

Pakistan: Pakistan, officially the Islamic Republic of Pakistan, is a country in South Asia... 

France: France, officially the French Republic, is a country in Western Europe... No Wikipedia article found for: flibbertigibbet 

## **Exercise 6 — Run the agent with real search** 

Re-run the questions from Exercise 3 with the real Wikipedia search tool. Compare the answers to what you got with the hardcoded search. 

Questions: 

"What is the capital of France?" 

"What is the population of Pakistan divided by the area of Pakistan?" "Who invented the telephone?" 

**Expected output (third question):** 

Question: Who invented the telephone? 

--- Step 1 --Thought: I'll search Wikipedia for the invention of the telephone. Action: search Input: telephone [Tool: search('telephone')] [Observation: The telephone is a telecommunications device that permits two or more users to conduct a conversation when they are too far apart to be heard directly. Alexander Graham Bell is often credited with patenting the first practical telephone in 1876...] 

--- Step 2 --Thought: I have the answer. Final Answer: Alexander Graham Bell is credited with inventing the telephone and patenting it in 1876. 

Notice the difference in answer quality compared to the hardcoded version. The Wikipedia tool can answer questions you never anticipated. 

## **4. Stopping Runaway Loops** 

## **Why loops run away** 

An agent loops when it can't find a satisfying answer. Common causes: 

The search tool returns nothing useful and the model keeps rephrasing the query The calculator returns an error and the model tries variations that also fail 

The model hallucinates a tool name, gets an "unknown tool" error, and keeps retrying The question has no answer in the available tools and the model won't admit it 

Without a guard, this burns your API quota and never returns. 

## **Three guards you should always have** 

**1. Step limit** — you already have this. Six steps is enough for simple agents; ten for complex ones. 

**2. Repetition detection** — if the model calls the same tool with the same input twice in a row, it's stuck. Break out of the loop. 

**3. Empty response guard** — if the model returns an empty string or whitespace, something has gone wrong. Treat it as a final answer of "I was unable to process this request." 

## **Exercise 7 — Add repetition detection** 

Extend your run_agent function to track tool calls. If the same (tool_name, tool_input) pair appears twice in a row, break the loop and return a message saying the agent got stuck. 

Test it by giving the agent a question your search tool can't answer: 

Run: "What is the population of the city of Zibbleforth?" 

**Expected output:** 

Question: What is the population of the city of Zibbleforth? --- Step 1 --Thought: I'll search for the population of Zibbleforth. Action: search Input: Zibbleforth [Tool: search('Zibbleforth')] [Observation: No Wikipedia article found for: Zibbleforth] --- Step 2 --Thought: Let me try a different search. Action: search Input: Zibbleforth city population [Tool: search('Zibbleforth city population')] [Observation: No Wikipedia article found for: Zibbleforth city population] --- Step 3 --Thought: I'll try once more. Action: search Input: Zibbleforth [Tool: search('Zibbleforth')] [Observation: No Wikipedia article found for: Zibbleforth] Agent stuck: repeated call to search('Zibbleforth'). Stopping. 

The repetition guard fires when the same call is detected. Without it, this would run until the step limit. 

## **Exercise 8 — Final stress test** 

Run all three guards against a set of edge cases. For each one, write down which guard fired (step limit, repetition, or empty response) and whether the agent handled it gracefully. 

Questions to run: 

- "What is the population of Zibbleforth?" — unknown place, repetition likely 

- "Summarise the entire history of the universe in one sentence." — no tool can help 

- "What is 1 divided by 0?" — calculator error 

**Expected output (third question):** 

Question: What is 1 divided by 0? 

--- Step 1 --Thought: I'll use the calculator. Action: calculator Input: 1 / 0 

[Tool: calculator('1 / 0')] [Observation: Error: division by zero] 

--- Step 2 --Thought: Division by zero is undefined in mathematics. Final Answer: 1 divided by 0 is undefined — division by zero is not a valid operation. 

A well-designed agent recovers from a tool error on the next step rather than crashing. Did yours? 

## **Check Your Understanding — Part 1** 

Before moving to the project, make sure you can answer these without looking: 

1. Why should every tool return a string, even if the result is a number? 

2. Your agent calls the same tool with the same input three times in a row. What is causing this and how does repetition detection fix it? 

3. What is the difference between your agent failing because of a bad tool and failing because of a bad system prompt? 

4. You add a fourth tool but forget to describe it in the system prompt. What happens when a user asks a question that requires it? 

5. A teammate suggests removing the step limit because "smart questions need more steps." What's the risk? 

## **5. Project — Document Q&A Web App** 

This is your second portfolio piece. By the end of today you'll have a working web app where anyone can upload a document and ask questions about it — with source citations on every answer. 

## **What you're building** 

A Streamlit web app that: 

Accepts a .txt file upload Chunks and indexes it into a persistent Chroma collection Takes questions from the user Returns answers grounded in the document with the source passages shown Handles edge cases cleanly — empty input, short documents, missing files, API errors 

This is a direct extension of the Day 9 Streamlit app. The difference is persistence, polish, and robustness. 

## **Project structure** 

Before writing a line of code, set up your folder: 

doc-qa/ ├── .env ├── .gitignore ├── requirements.txt ├── app.py └── chroma_db/        ← created automatically when you run the app 

Your .gitignore should exclude .env , __pycache__ , *.pyc , and the chroma_db/ folder — the database is local and shouldn't be committed. 

## **Exercise 9 — Plan your app before building it** 

Write down (on paper or in a notes file) answers to these questions before touching code: 

What happens when a user uploads a new file over an existing one? Should the old collection be cleared or kept? How will you prevent the app from re-indexing the same document every time the user types a character? What should the user see while the document is being indexed? What should happen if the API call fails mid-answer? 

Where should the source citations appear — above or below the answer? 

There are no wrong answers here. The point is to make deliberate choices before coding so you're not making them under pressure when something breaks. 

## **Exercise 10 — Build the ingestion pipeline** 

Build the file upload and indexing section of app.py first, completely separate from the question-answering part. Get this working in the browser before moving on. Your ingestion pipeline should: 

Show a file uploader for .txt files Read and decode the file when uploaded Show a document preview in a collapsible section (use st.expander ) Chunk the text using overlapping sentence chunks (from Day 8) Embed and store in a **persistent** Chroma collection using PersistentClient Use get_or_create_collection — if the same file has been uploaded before, don't re-index it Show the chunk count after indexing with st.success Cache the embedding model with @st.cache_resource so it isn't reloaded on every render 

**Expected output in the browser:** 

[File uploader widget] 

� Indexed 24 chunks from my_document.txt 

▶ Document preview 

The document begins with... 

## **Exercise 11 — Build the Q&A section** 

Add the question input and answer display below the ingestion section. This only appears once a document has been successfully indexed. 

Your Q&A section should: 

Show a text input for the user's question, disabled until a document is loaded On question submission, retrieve the top 3 most relevant chunks from Chroma Build a prompt with the retrieved context and send it to Gemini Display the answer clearly 

Display each source chunk below the answer, numbered and formatted Show a spinner while the answer is being generated Handle API errors with st.error and st.stop() 

**Expected output in the browser:** 

Your question: [text input] 

## Answer: 

Python was created by Guido van Rossum and first released in 1991... 

## Sources: 

[1] Python was created by Guido van Rossum and first released in 1991. It is an interpreted, high-level, general-purpose programming language... 

- [2] Python 2 reached end of life in 2020 and Python 3 is the current standard. Popular Python frameworks include Django and Flask... 

- [3] TensorFlow and PyTorch are the dominant libraries for deep learning in Python. Python is consistently ranked as one of the most popular... 

## **Exercise 12 — Add the polish layer** 

These additions move the app from "it works" to "it's good": 

## **A — Clear collection button** 

Add a button labelled "Clear and re-index" that deletes the existing Chroma collection and re-indexes the current document. Useful when the user uploads a new version of the same file. 

**B — Question history** 

Use st.session_state to store previous questions and answers in the session. Display them above the current question input so the user can scroll back through the conversation. **C — Short document warning** If the chunk count is below 5, show a st.warning telling the user the document is very short and results may be limited. 

## **D — Empty question guard** 

If the user submits an empty question (just hits Enter), show st.info("Please enter a question.") and don't call the API. 

Implement all four, then run through this checklist manually: 

Upload a document — chunk count appears Ask a question that's in the document — relevant answer with sources Ask a question not in the document — model says so Submit an empty question — info message, no API call Upload a very short document — warning appears Click "Clear and re-index" — collection resets 

**Exercise 13 — Write the README** 

Before pushing to GitHub, write a README.md that covers: 

What the app does (one paragraph) 

- A screenshot or description of the interface 

Setup instructions: clone, .env file, pip install -r requirements.txt , streamlit run app.py Known limitations: only .txt files, English language, context window constraints 

The README is part of the project. A recruiter or collaborator who opens your repo should understand what the app does and how to run it in under two minutes. 

## **Check Your Understanding — Part 2** 

Before moving on, make sure you can answer these without looking: 

1. Why use PersistentClient here but Client() was fine in earlier exercises? 

2. What is st.session_state and why do you need it to store question history? 

3. Your app re-indexes the document every time the user types a character. What is the likely cause and how do you fix it? 

4. The user uploads a new document but the old answers are still showing in the history. Is this a bug? How would you handle it? 

5. You have the full pipeline working locally. What's the one thing you must check before pushing to GitHub? 

