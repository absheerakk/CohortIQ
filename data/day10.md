## **Day 10 — Tools & the ReAct Idea** 

RAG gives the model knowledge. Today you give it the ability to act. 

**What you're bringing in:** calling the Gemini API with a system prompt, prompt engineering, how next-token prediction works (Days 3–4). Agents are built on top of these fundamentals — nothing new to install today. 

## **1. What Makes Something an "Agent"** 

## **The difference between a chatbot and an agent** 

A chatbot receives a question and generates an answer. That's it — the model produces text and stops. 

An agent can do more. It can decide to take an action, observe the result of that action, and use that result to decide what to do next. The model isn't just generating an answer — it's participating in a loop. 

||**Chatbot**|**Agent**|
|---|---|---|
|Input|Question|Question|
|Process|Generate answer|Reason→Act→Observe→<br>Repeat|
|Output|Text|Text + actions taken|
|Can use tools?|No|Yes|
|Knows current<br>info?|No (training<br>cutoff)|Yes (via tools)|



## **What a "tool" is** 

A tool is just a Python function. You give the model a description of what the function does, and the model can decide to call it when it needs something the function provides. 

Examples: 

- A calculator(expression) function for maths 

- A search(query) function for current information 

- A read_file(path) function for accessing documents 

- A send_email(to, subject, body) function for taking real-world actions 

The model doesn't run the function itself — it outputs a structured decision saying "I want to call this tool with these arguments." Your code runs the function and gives the result back to the model. 

## **Exercise 1 — See the problem tools solve** 

Send these three questions to the Gemini API and print each answer: 

- "What is 17 multiplied by 38, then divided by 4? Show your working." 

- "What is the square root of 1764?" 

- "What day of the week is 15 August 2047?" 

Use model.generate_content(question) inside a loop, same as you've done before. 

**Expected output (approximate — answers may vary):** 

- Q: What is 17 multiplied by 38, then divided by 4? Show your working. 

- A: 17 * 38 = 646. 646 / 4 = 161.5 

- Q: What is the square root of 1764? 

- A: The square root of 1764 is 42. 

- Q: What day of the week is 15 August 2047? 

- A: 15 August 2047 falls on a Thursday. 

Verify each answer manually. At least one is likely wrong — the model is predicting tokens, not computing. That's the problem a calculator tool solves. 

**2. The ReAct Loop — Reason, Act, Observe** 

## **The idea** 

ReAct stands for **Reason → Act → Observe** . It's the loop at the heart of every agent: 

1. **Reason** — the model thinks about what it needs to do next 

2. **Act** — it calls a tool 

3. **Observe** — it receives the tool's output 

4. **Repeat** — it reasons again using the observation, until it has a final answer 

A concrete example: 

Question: "What is the population of Pakistan multiplied by 3?" 

Reason:  I need the population of Pakistan. I'll search for it. Act:     search("population of Pakistan 2024") Observe: "Pakistan's population is approximately 240 million." Reason:  Now I can compute 240,000,000 × 3. I'll use the calculator. Act:     calculator("240000000 * 3") Observe: "720000000" Reason:  I have everything I need. Final:   "The population of Pakistan multiplied by 3 is approximately 720 million." 

The model never computes the maths or fetches the population itself. It reasons about what it needs, delegates to tools, and synthesises a final answer from what comes back. 

## **How you implement it** 

You implement the loop manually in Python. Your code: 

1. Sends the question to the model 

2. Parses the model's response to see if it wants to call a tool 

3. If yes: runs the tool, sends the result back to the model 

4. If no: the model has a final answer — return it 

## **3. Hand-Writing a Minimal ReAct Loop** 

## **The format** 

The model outputs its reasoning and tool calls as structured text. You'll use this format throughout: 

Thought: I need to calculate 17 * 38. Action: calculator Input: 17 * 38 [your code runs calculator("17 * 38") and gets 646] 

Observation: 646 Thought: I have the answer. Final Answer: 17 multiplied by 38 is 646. 

Your code parses the model's response line by line, looking for Action: , Input: , and Final Answer: to decide what to do next. 

## **Exercise 2 — Define and test the tools** 

Write two functions: calculator(expression) and search(query) . 

For calculator : use Python's eval() with a restricted namespace that only allows math functions — no builtins. Return the result as a string, or an error message if it fails. 

For search : use a plain dictionary of hardcoded responses keyed by topic. If the query matches a key, return the value. If not, return "No result found for: {query}" . Include at minimum: population of Pakistan, capital of France, height of Mount Everest, speed of light, Pakistan independence, area of Pakistan. 

Test both functions directly before building the loop. 

## **Expected output:** 

646 

12.0 

Pakistan's population is approximately 240 million (2024). The capital of France is Paris. No result found for: weather in tokyo 

Always test tools in isolation first. A bug in a tool produces a confusing agent failure that's hard to trace. 

## **Exercise 3 — Write the system prompt** 

## Write a SYSTEM_PROMPT string that tells the model: 

It has two tools: calculator and search , with a one-line description and example input for each The exact format to use when calling a tool (Thought / Action / Input on separate lines) The exact format to use when it has a final answer (Thought / Final Answer) Never to guess at numbers — always use the calculator 

Print it and read it carefully. 

## **Expected output:** 

You are an agent that can use tools to answer questions. 

You have access to these tools: 

- calculator: Evaluates a mathematical expression. Use for any arithmetic. 

Input: a mathematical expression, e.g. "17 * 38" or "sqrt(144)" 

- search: Searches for factual information. 

Input: a short search query, e.g. "population of Pakistan" 

To use a tool: 

Thought: <your reasoning> Action: <tool name> Input: <tool input> 

When you have a final answer: Thought: <your reasoning> Final Answer: <your answer> 

Always use tools for calculations and facts. Never guess at numbers. 

Every line matters. The format instructions are what your parser will rely on — if they're ambiguous, the model will deviate and parsing will break. 

## **Exercise 4 — Write the parser** 

Write a parse_response(text) function that reads the model's response line by line and returns either: 

- ("tool", tool_name, tool_input) if it finds Action: and Input: lines 

- ("final", answer) if it finds a Final Answer: line 

- ("final", text) as a fallback if neither is found 

Test it on these three inputs: 

test_responses = [ 

- "Thought: I need to calculate this.\nAction: calculator\nInput: 17 * 38", 

- "Thought: I have the answer.\nFinal Answer: The result is 646.", 

- "I don't know what to do.", 

] 

**Expected output:** 

Response: 'Thought: I need to calculate this.\nAction: calculator\nInput: 17 * 38' Parsed:   ('tool', 'calculator', '17 * 38') 

Response: 'Thought: I have the answer.\nFinal Answer: The result is 646.' Parsed:   ('final', 'The result is 646.') Response: "I don't know what to do." Parsed:   ('final', "I don't know what to do.") 

## **Exercise 5 — Assemble the full loop** 

Write a run_agent(question, max_steps=6) function that: 

1. Creates a Gemini model with your SYSTEM_PROMPT as the system_instruction 

2. Starts a history list with the user's question 

3. Loops up to max_steps times: 

Sends history to the model, gets a reply Prints the step number and the model's reply Parses the reply If final: prints and returns the answer If tool: looks up the tool in a TOOLS dict, runs it, prints the observation, appends it to history as a user message 

4. Returns a "step limit reached" message if it never finishes 

Then call it with: 

run_agent("What is the population of Pakistan multiplied by 2?") 

## **Expected output:** 

Question: What is the population of Pakistan multiplied by 2? 

--- Step 1 --Thought: I need to find the population of Pakistan first. Action: search Input: population of Pakistan 

[Tool: search('population of Pakistan')] [Observation: Pakistan's population is approximately 240 million (2024).] 

--- Step 2 --Thought: Now I can calculate 240 million multiplied by 2. Action: calculator Input: 240000000 * 2 

[Tool: calculator('240000000 * 2')] [Observation: 480000000] 

--- Step 3 --Thought: I have the result. Final Answer: The population of Pakistan multiplied by 2 is approximately 480 million. 

Watch the loop carefully. Two tool calls, then a final answer. That's the full ReAct cycle working. 

## **Exercise 6 — Test with multi-step questions** 

Run your agent on these three questions: 

"What is the height of Mount Everest in metres divided by 3?" 

"How many years have passed since Pakistan gained independence?" "What is the area of Pakistan divided by its population?" 

**Expected output (third question):** 

Question: What is the area of Pakistan divided by its population? 

--- Step 1 --Thought: I need the area of Pakistan. Action: search Input: area of Pakistan 

[Tool: search('area of Pakistan')] [Observation: Pakistan has a total area of approximately 881,913 square kilometres.] 

--- Step 2 --Thought: I need the population of Pakistan. Action: search Input: population of Pakistan 

[Tool: search('population of Pakistan')] [Observation: Pakistan's population is approximately 240 million (2024).] 

--- Step 3 --Thought: Now I can divide the area by the population. Action: calculator Input: 881913 / 240000000 

[Tool: calculator('881913 / 240000000')] [Observation: 0.003674637...] 

--- Step 4 --Thought: I have the result. Final Answer: The area of Pakistan per person is approximately 0.00367 square kilometres, or about 3.67 square metres per person. 

For each question: how many steps did it take? Did it use the tools in the right order? Is the final answer correct? 

## **4. When and Why Agents Go Wrong** 

## **The four main failure modes** 

## **1. The model ignores the format** 

The model doesn't output Action: and Input: on separate lines — your parser misses the tool call and falls through to a "final answer" that's actually the model guessing. Fix: make format instructions in the system prompt very explicit. 

## **2. The model calls a tool that doesn't exist** 

The model hallucinates a tool name like web_search when your dict only has search . Your code should check if tool_name not in TOOLS and return a clear error so the model can recover. 

## **3. Infinite loops** 

Without a max_steps limit, an agent that can't find an answer will loop forever, burning your API quota. Always set a cap. Six steps is enough for simple agents. 

## **4. Wrong tool input** 

The model calls calculator("population of Pakistan * 2") without searching first. The expression fails, the model gets an error, and may loop trying to fix it. Fix: clear system prompt instructions — "use search for facts, calculator for arithmetic only." 

## **Exercise 7 — Break the agent and understand why** 

Run your agent on each of these: 

- "What is the GDP of Denmark?" — outside the search tool's knowledge 

- "What is 999 multiplied by 888?" — pure calculation, no search needed 

- "What is the answer to everything?" — ambiguous, no useful tool result 

**Expected output (first question):** 

Question: What is the GDP of Denmark? 

--- Step 1 --Thought: I'll search for the GDP of Denmark. Action: search Input: GDP of Denmark 

[Tool: search('GDP of Denmark')] [Observation: No result found for: GDP of Denmark] 

--- Step 2 --Thought: The search didn't return a result. I don't have this information. Final Answer: I wasn't able to find the GDP of Denmark using the available tools. 

For each test write down: did the agent handle it gracefully? Did it stay within the step limit? If it failed — was the failure in the parser, the tools, or the model's reasoning? 

## **Check Your Understanding** 

Before moving to Day 11, make sure you can answer these without looking: 

1. What is the difference between a chatbot and an agent? 

2. In the ReAct loop, who runs the tool — the model or your code? 

3. Why does every agent need a max_steps limit? 

4. The model outputs Action: google_search but your tools dict only has search . What happens, and how should your code handle it? 

5. Your agent takes 5 steps to answer "What is 2 + 2?". What does this suggest about your system prompt? 

