## **Day 4 — Roles, History, Prompt Engineering & the Chat CLI Project** 

Today covers three things: how to talk to the model properly using roles, how to do prompt engineering, and then you put it all together into your first real portfolio project. 

**What you're bringing in:** variables, loops, functions, try/except , calling the Gemini API, loading keys from .env , and how tokens and temperature work (Days 1–3). 

## **1. The Chat API — Roles, History & JSON** 

## **Why roles exist** 

So far you've been sending a single string to the model. Real applications need more control — you want to give the model a personality, pass it conversation history, and get structured data back. Roles are how you do all of that. 

There are three roles: 

|**Role**|**Who it is**|**What it's for**|
|---|---|---|
|system|You, the developer|Set the model's behaviour, personality, and rules before the conversation<br>starts|
|user|The human|The questions and messages coming in|
|assistant|The model|The model's previous replies (used when sending history)|



The system message is invisible to the user but shapes every response. Think of it as the briefing you give the model before it goes to work. 

## **Sending a system prompt** 

import os import google.generativeai as genai from dotenv import load_dotenv load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) model = genai.GenerativeModel( model_name="gemini-1.5-flash", system_instruction="You are a concise assistant. Answer in one sentence only.", ) response = model.generate_content("What is machine learning?") print(response.text) 

Run it, then remove the system_instruction and run it again. Notice how much the length and tone change. 

## **Multi-turn conversation history** 

The Gemini API has no memory between calls. If you want it to remember what was said earlier, you have to send the full conversation history every time. 

History is a list of dicts, each with a role and parts : 

history = [ {"role": "user",      "parts": ["My name is Shahadil."]}, {"role": "model",     "parts": ["Nice to meet you, Shahadil!"]}, {"role": "user",      "parts": ["What is my name?"]}, ] response = model.generate_content(history) print(response.text)  # Should say Shahadil 

Note: Gemini uses "model" where other APIs use "assistant" — same concept, different label. 

**Asking for JSON output** 

Sometimes you want structured data back instead of prose. Tell the model exactly what format you need and it will usually comply — especially at low temperature. 

import json model = genai.GenerativeModel( model_name="gemini-1.5-flash", system_instruction=( "You are a data extraction assistant. " "Always respond with valid JSON only. No explanation, no markdown." ), generation_config=genai.types.GenerationConfig(temperature=0), ) prompt = ( "Extract the name, email, and city from this text: " "'Hi I am Sara, reach me at sara@email.com, based in Karachi.'" " Return JSON with keys: name, email, city." ) response = model.generate_content(prompt) try: data = json.loads(response.text) print(data) except json.JSONDecodeError: print("Model didn't return valid JSON:") print(response.text) 

## **Exercises — Roles, History & JSON** 

**Exercise 1 — System prompt changes everything** 

Run the same question with three different system instructions and print all three responses side by side. 

import os import google.generativeai as genai from dotenv import load_dotenv 

load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) question = "What is the internet?" 

personas = { "One sentence only":        "Answer every question in exactly one sentence.", "Explain to a 7-year-old":  "You explain everything as if talking to a 7-year-old child.", "Senior engineer":          "You are a senior software engineer. Be technical and precise.", } for label, instruction in personas.items(): model = genai.GenerativeModel( model_name="gemini-1.5-flash", system_instruction=instruction, ) response = model.generate_content(question) print(f"--- {label} ---") print(response.text.strip()) print() 

Same question, three very different answers. This is what system prompts give you. 

**Exercise 2 — Build a real multi-turn conversation** 

Write a script that maintains a history list and adds each exchange to it, so the model actually remembers what was said. 

import os import google.generativeai as genai from dotenv import load_dotenv load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

model = genai.GenerativeModel( model_name="gemini-1.5-flash", system_instruction="You are a helpful assistant with a good memory.", ) history = [] turns = [ "My favourite programming language is Python.", "I am learning AI engineering.", "What is my favourite programming language?", "What am I currently learning?", ] for user_message in turns: history.append({"role": "user", "parts": [user_message]}) response = model.generate_content(history) reply = response.text.strip() history.append({"role": "model", "parts": [reply]}) print(f"User:  {user_message}") print(f"Model: {reply}") print() 

Did the model remember the facts from earlier turns? What happens if you remove the history and just send the last question on its own? 

**Exercise 3 — Extract structured data with JSON output** 

Send the model a block of messy text and get clean structured data back. 

import os import json import google.generativeai as genai from dotenv import load_dotenv 

## load_dotenv() 

genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

model = genai.GenerativeModel( 

model_name="gemini-1.5-flash", 

system_instruction="You are a data extraction tool. Always return valid JSON only. No markdown, no explanation.", generation_config=genai.types.GenerationConfig(temperature=0), 

) 

records = [ 

"Ahmed, 28, works as a backend developer in Lahore. Email: ahmed@dev.pk", 

"Sara is a UX designer based in Karachi, she's 31. Contact her at sara@ux.io", "Bilal (bilal@ml.com) is 25, studying machine learning in Islamabad", ] 

for record in records: prompt = ( 

f"Extract the name, age, city, role, and email from this text. " f"Return JSON with keys: name, age, city, role, email.\n\n{record}" ) 

response = model.generate_content(prompt) 

try: 

data = json.loads(response.text) print(data) except json.JSONDecodeError: print(f"Failed to parse JSON for: {record}") print(response.text) print() 

Did it extract all fields correctly? What happened with fields that weren't clearly stated in the text? 

## **2. Prompt Engineering** 

## **What it actually is** 

Prompt engineering is the practice of writing inputs to an LLM in a way that reliably produces the output you want. It's not magic — it's applying what you learned in Day 3. The model continues your text. The better you frame what kind of document you're starting, the better the continuation. 

## **The core techniques** 

**Zero-shot** — just ask, no examples: 

"Classify this review as positive or negative: 'Great product, arrived fast.'" 

**Few-shot** — show examples before asking: 

"Classify as positive or negative.\nExamples:\n'Loved it!' → positive\n'Broke after a day' → negative\nNow classify: 'Decent quality but slow shipping.'" 

**Chain-of-thought** — tell it to think before answering: 

"Think step by step, then give your final answer." 

**Persona** — give it a role: 

"You are an experienced tax accountant. Explain..." 

**Structured output** — specify the exact format: 

"Return your answer as JSON with keys: verdict, confidence, reason." 

## **What makes a prompt reliable** 

**Be specific** — vague prompts get vague answers 

**Give context** — the model doesn't know your situation unless you tell it **Show the format** — if you want bullet points, use bullet points in your example **Use temperature deliberately** — creative tasks: higher; factual/structured: lower **Give it an escape hatch** — "If you are not sure, say so" reduces hallucination 

## **Exercises — Prompt Engineering** 

**Exercise 4 — Compare zero-shot vs few-shot** 

The same task, two approaches. See which one is more accurate and consistent. 

import os import google.generativeai as genai from dotenv import load_dotenv 

load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

model = genai.GenerativeModel( model_name="gemini-1.5-flash", generation_config=genai.types.GenerationConfig(temperature=0), ) reviews = [ "The battery lasts forever, really impressed.", "Stopped working after two weeks. Total waste.", "It is okay I guess, nothing special.", "Absolutely love it, using it every day!", "Not what I expected based on the description.", ] 

zero_shot = "Classify this review as positive, negative, or neutral. Reply with one word only.\n\nReview: {review}" 

few_shot = """Classify this review as positive, negative, or neutral. Reply with one word only. 

Examples: Review: "Best purchase I have made this year." → positive Review: "Completely fell apart after one use." → negative Review: "Does the job, nothing more." → neutral 

Review: {review}""" 

print(f"{'Review':<50} {'Zero-shot':>12} {'Few-shot':>12}") print("-" * 76) 

for review in reviews: 

r0 = model.generate_content(zero_shot.format(review=review)).text.strip() rf = model.generate_content(few_shot.format(review=review)).text.strip() print(f"{review:<50} {r0:>12} {rf:>12}") 

Did few-shot change any of the answers? Which reviews were ambiguous and which approach handled them better? 

**Exercise 5 — Chain-of-thought vs direct answer** 

For reasoning tasks, telling the model to think before answering often improves accuracy. 

import os 

import google.generativeai as genai 

from dotenv import load_dotenv 

load_dotenv() 

genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

model = genai.GenerativeModel("gemini-1.5-flash") 

problem = ( 

"A shop sells apples for Rs 40 each and oranges for Rs 25 each. " 

"Ali buys 3 apples and 5 oranges. He pays with a Rs 500 note. " "How much change does he get?" ) 

direct = f"{problem}\n\nWhat is the answer?" 

cot    = f"{problem}\n\nThink through this step by step, then give the final answer." 

print("--- Direct answer ---") 

print(model.generate_content(direct).text.strip()) print("\n--- Chain-of-thought ---") print(model.generate_content(cot).text.strip()) 

Did chain-of-thought get the right answer? Did the direct approach? Run each a few times — is one more consistent than the other? 

**Exercise 6 — Reusable prompt templates** 

Hard-coding prompts everywhere makes them impossible to maintain. Write a function that builds prompts from a template, then use it. 

import os 

import google.generativeai as genai from dotenv import load_dotenv 

## load_dotenv() 

genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

model = genai.GenerativeModel( 

model_name="gemini-1.5-flash", generation_config=genai.types.GenerationConfig(temperature=0.3), ) 

def summarise_prompt(text, max_sentences=3, audience="general"): return ( 

f"Summarise the following text in {max_sentences} sentences or fewer. " f"Write for a {audience} audience. Be clear and direct.\n\n{text}" ) 

texts = [ ( "Machine learning is a subset of artificial intelligence that gives systems " "the ability to learn from data without being explicitly programmed. " "It focuses on building programs that improve automatically through experience. " "Applications include image recognition, language translation, and recommendation systems.", 2, "non-technical", ), ( "Gradient descent is an optimisation algorithm used to minimise a function by " "iteratively moving in the direction of steepest descent as defined by the " "negative of the gradient. It is widely used in training neural networks.", 2, "technical", ), ] 

for text, sentences, audience in texts: 

prompt = summarise_prompt(text, max_sentences=sentences, audience=audience) response = model.generate_content(prompt) print(f"Audience: {audience}") print(response.text.strip()) print() 

Notice how the same template, with different parameters, produces different outputs. This is how real applications manage prompts at scale. 

## **3. Week 1 Project — "Ask the AI" CLI Tool** 

Now put everything together. You know the API, roles, history, and prompt engineering. Build a proper CLI chatbot that uses all of it. 

## **What you're building** 

A command-line chatbot with a persistent conversation 

A system prompt that gives it a clear personality Multi-turn memory — it remembers what was said earlier in the session Clean error handling Safe to push to GitHub (no leaked keys) 

## **Project setup** 

Create a new folder called ask-the-ai and set it up the same way you did in earlier days — .env for your key, .gitignore to keep it out of Git, and requirements.txt listing your dependencies. 

**Step 1 — Decide on a persona** 

Before touching code, write your system prompt in plain English. A specific persona produces a far better chatbot than a vague one. 

Bad: "You are a helpful assistant." 

Good: "You are a sharp, friendly assistant. You give direct answers without padding. If you don't know something, say so honestly instead of guessing." 

Write yours down. You'll paste it into SYSTEM_PROMPT in the next step. 

## **Step 2 — Structure your main.py** 

Your script needs three things: 

**A load_model() function** that: 

Calls load_dotenv() 

Reads GEMINI_API_KEY from the environment Exits with a clear error message if the key is missing 

Configures genai and returns a GenerativeModel with your system_instruction 

**A chat() function** that: 

Takes the model, the history list, and the user's message 

Appends the user message to history as {"role": "user", "parts": [message]} Calls model.generate_content(history) Appends the model's reply to history as {"role": "model", "parts": [reply]} Returns the reply text 

Wraps the API call in try/except — if it fails, remove the user message from history and return a friendly error string 

**A main() function** that: 

Calls load_model() and creates an empty history list 

Runs a while True loop 

Skips empty input with continue Breaks on "quit" and prints how many messages were exchanged Otherwise calls chat() and prints the reply 

## **Step 3 — Test it manually** 

Once your script runs, verify each of these: 

Tell it your name in one message, then ask "what is my name?" two messages later — it should remember Ask it something obscure or made up — does it admit uncertainty or confabulate confidently? Hit Enter without typing anything — it should not send a blank message or crash Add a wrong character to your API key in .env , run it — you should see your error message, not a Python traceback 

## **Stretch Goals** 

## **Stretch 1 — Change the persona** 

Rewrite SYSTEM_PROMPT so the chatbot is something specific: a Python tutor, a recipe suggester, a travel guide for Pakistan. Notice how the same code produces a completely different product just by changing those lines. 

## **Stretch 2 — Add a /clear command** 

Let the user type /clear to wipe the conversation history and start fresh without quitting. The history list goes back to [] and a confirmation message is printed. 

## **Stretch 3 — Save the conversation to a file** 

When the user types quit , write the full conversation to chat_log.txt — each turn labelled clearly. Add chat_log.txt to .gitignore . 

## **Check Your Work** 

The chatbot remembers what you said earlier in the conversation A broken API key shows a useful error, not a stack trace Empty input doesn't crash or send a blank message quit exits cleanly with a message count .env is NOT on GitHub README is visible on the repo and explains how to run it 

