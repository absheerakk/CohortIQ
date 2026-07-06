## **Day 3 — How LLMs Actually Work** 

No heavy math. Just the mental models that will make you a better AI engineer. 

**What you already know coming in:** variables, loops, functions, dictionaries, and how to send one question to the Gemini API and print the answer (Day 2). That's all you need for today. 

## **1. Tokens and Context Windows** 

## **What is a token?** 

LLMs don't read words — they read **tokens** . A token is roughly a chunk of text, somewhere between a character and a word. 

Some rules of thumb: 

- Common short words ( the , is , on ) → usually 1 token each 

- Longer or rarer words ( unbelievable , tokenization ) → often split into 2–3 tokens 

- Numbers, punctuation, and code → can be very token-hungry 

- ~100 tokens ≈ ~75 words in English (a useful approximation) 

**Why it matters:** You're billed per token. You're also _limited_ per token. 

## **The context window** 

Every model has a **context window** — a maximum number of tokens it can "see" at once. Think of it like a whiteboard. Everything has to fit on the board: your question, any background you gave it, and the answer it's writing. When things get too long, older content falls off the edge — the model genuinely cannot see it anymore. 

**Model Approximate context window** Gemini 1.5 Flash ~1,000,000 tokens (~750,000 words) GPT-4o ~128,000 tokens Llama 3 8B (local) ~8,000 tokens 

**Practical implication:** smaller or cheaper models fill up fast. Knowing how many tokens your input uses is a real engineering concern. 

## **Exercises — Tokens & Context Windows** 

## **Exercise 1 — Count tokens with the Gemini API** 

The Gemini API can count tokens for you before you send a request. Run this script and observe the results. 

import os import google.generativeai as genai from dotenv import load_dotenv 

load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

model = genai.GenerativeModel("gemini-1.5-flash") 

strings = [ "Hello, world!", "The quick brown fox jumps over the lazy dog.", "Supercalifragilisticexpialidocious is a word from a 1964 film.", "x=1;y=2;z=x+y;print(z)", "Patient presents with a fever of 38.9 degrees, dry cough, and fatigue for 3 days.", ] 

for s in strings: result = model.count_tokens(s) print(f"{result.total_tokens:>4} tokens | {s}") 

Look at the numbers. Which strings used more tokens than you expected? Is prose or code more token-hungry per character? 

## **Exercise 2 — Watch the token count grow** 

This script simulates what happens as a conversation grows — it keeps adding a message to a list and counts the total tokens after each addition. Watch how quickly the number climbs. 

import os import google.generativeai as genai from dotenv import load_dotenv 

load_dotenv() 

genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

model = genai.GenerativeModel("gemini-1.5-flash") 

TOKEN_LIMIT = 300  # pretend this is our context window 

message = "The customer asked about the refund policy and we explained it takes 5 to 7 business days." 

messages = [] 

for turn in range(1, 20): 

messages.append(message) combined = " ".join(messages) 

total = model.count_tokens(combined).total_tokens 

print(f"Turn {turn:>2} | Tokens so far: {total}") 

if total >= TOKEN_LIMIT: 

print(f"\nHit the limit at turn {turn}. Older messages would start falling off here.") break 

How many turns before it fills up? What would happen to the conversation after that point? 

## **2. What "Next-Word Prediction" Really Means** 

At its core, an LLM does one thing: **given everything so far, predict what token comes next.** 

No lookup table. No search engine. No understanding in the human sense. The model picks one token, appends it, then picks the next one. Every word you read in a response was chosen one token at a time. 

## **So why does it seem intelligent?** 

To get good at predicting the next word across trillions of examples of human writing, the model had to develop internal patterns for facts, reasoning, grammar, style, and world knowledge. These weren't programmed — they emerged from training. 

A useful mental model: the model has compressed a huge slice of human text into itself. When you prompt it, you're asking it to _continue your text_ in a way consistent with everything it learned. The way you frame your prompt changes what kind of document the model thinks it's continuing — and that changes the response dramatically. 

## **Exercises — Next-Word Prediction** 

## **Exercise 3 — See how framing changes the response** 

The same underlying question, framed two different ways, gets two very different responses. This is because the model is continuing different kinds of "documents." 

import os import google.generativeai as genai from dotenv import load_dotenv 

load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

model = genai.GenerativeModel("gemini-1.5-flash") 

prompts = { "Clinical framing": "Patient presents with fever, cough, and fatigue.", "Casual framing":   "I have a fever, cough, and fatigue. What should I do?", } 

for label, prompt in prompts.items(): response = model.generate_content(prompt) print(f"--- {label} ---") print(response.text) print() 

Write down: how do the tone, length, and structure differ? Both prompts describe the same symptoms — why does the framing matter so much? 

## **Exercise 4 — Sentence completion** 

Send the model incomplete sentences and see how it finishes them. This makes next-token prediction visible — you're watching it do the thing. 

import os import google.generativeai as genai from dotenv import load_dotenv 

load_dotenv() 

genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

model = genai.GenerativeModel("gemini-1.5-flash") 

fragments = [ "The mitochondria is the powerhouse of the", "To be, or not to be, that is the", "In Python, to open a file you use the", "The capital of Australia is", ] 

for fragment in fragments: 

response = model.generate_content(fragment) 

print(f"PROMPT:     {fragment}") print(f"COMPLETION: {response.text.strip()}") print() 

Before running: write down your own guess for each one. After running: did the model match? Note — the capital of Australia is Canberra, not Sydney. Did it get that one right? 

## **3. Temperature and Randomness** 

When the model picks the next token it has a ranked list of possibilities. **Temperature** controls how that list is used. 

**Low temperature (e.g. 0.1)** — the model sticks heavily to its top choice. Outputs are consistent and predictable. Good for factual tasks. 

**High temperature (e.g. 1.4)** — lower-ranked tokens get more of a chance. Outputs are more varied and surprising. Good for creative tasks, but less reliable for facts. 

**Temperature = 0** — always picks the single most likely token. Run the same prompt twice and get the same answer. 

**Task Recommended temperature** 

Extracting data from a document 0 – 0.2 

Answering factual questions 0.2 – 0.4 Drafting an email 0.5 – 0.7 Brainstorming or creative writing 0.8 – 1.2 

## **Exercises — Temperature and Randomness** 

## **Exercise 5 — Run the same factual prompt at different temperatures** 

import os import google.generativeai as genai from dotenv import load_dotenv 

load_dotenv() 

genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

prompt = "What is the capital of Australia?" 

for temperature in [0.1, 1.4]: print(f"\n{'='*50}") print(f"Temperature: {temperature}") print(f"{'='*50}") for run in range(1, 6): model = genai.GenerativeModel( "gemini-1.5-flash", generation_config=genai.types.GenerationConfig(temperature=temperature), ) response = model.generate_content(prompt) print(f"Run {run}: {response.text.strip()}") 

Did the answer stay the same at low temperature? Did it ever change at high temperature? Did the model ever say Sydney? 

## **Exercise 6 — Temperature and creativity** 

Same pattern, creative prompt this time. 

import os import google.generativeai as genai from dotenv import load_dotenv 

load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

prompt = "Write the opening sentence of a mystery novel set in a rainy city." 

for temperature in [0.1, 1.4]: print(f"\n{'='*50}") print(f"Temperature: {temperature}") print(f"{'='*50}") for run in range(1, 6): model = genai.GenerativeModel( "gemini-1.5-flash", generation_config=genai.types.GenerationConfig(temperature=temperature), ) response = model.generate_content(prompt) print(f"Run {run}: {response.text.strip()}") print() 

Which temperature produced more interesting sentences? Which were more consistent? Which would you want if you needed the output to be grammatically correct every time? 

## **Exercise 7 — Your own temperature explorer** 

Put it together: write a script that takes a prompt you type, runs it at three temperatures, and prints all three responses labelled. 

import os import google.generativeai as genai from dotenv import load_dotenv 

load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

prompt = input("Enter a prompt: ") 

for temperature in [0.0, 0.5, 1.0]: model = genai.GenerativeModel( "gemini-1.5-flash", generation_config=genai.types.GenerationConfig(temperature=temperature), ) response = model.generate_content(prompt) print(f"\n--- Temperature {temperature} ---") print(response.text.strip()) 

Try it with at least three prompts: one factual question, one creative request, one asking for a list. Which temperature felt best for each? 

## **4. Strengths, Limits, and Why Models Hallucinate** 

## **What LLMs are genuinely good at** 

- Summarising, rewriting, translating, and reformatting text 

- Explaining concepts at adjustable depth 

- Generating fluent, well-structured prose quickly 

- Writing code in well-represented languages 

- Following clear, structured instructions 

## **Where they reliably struggle** 

- **Arithmetic** — they predict tokens, they don't compute 

- **Precise facts** — no memory, no database; just patterns learned during training 

- **Knowing what they don't know** — no reliable self-awareness of their own gaps 

- **Events after their training cutoff** — they genuinely have no information 

## **Why hallucination happens** 

The model's job is to produce the most plausible continuation of your prompt. When it doesn't know something, it doesn't stop — it keeps producing a plausible-sounding continuation anyway, because that's what it was trained to do. 

Two key causes: 

**1. The prompt creates pressure toward a confident answer.** Asking "What year did X happen?" pushes the model to produce a year. A confident-sounding wrong answer is statistically "more plausible" than "I don't know." 

**2. Training data had gaps.** The model may have learned wrong things, or never learned some things at all — and has no way to tell you which is which. 

**The practical lesson:** never trust an LLM as a source of truth for specific facts without verifying. Use it to reason, draft, and summarise — then check what matters. 

## **Exercises — Strengths, Limits, and Hallucination** 

## **Exercise 8 — Trigger a hallucination on purpose** 

Ask about an event that doesn't exist. The model has no correct answer — watch what it does. 

import os 

import google.generativeai as genai from dotenv import load_dotenv 

load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

# This event does not exist 

prompt = "Who won the 1987 Groznian Regional Chess Championship?" 

for run in range(1, 4): model = genai.GenerativeModel( "gemini-1.5-flash", generation_config=genai.types.GenerationConfig(temperature=0.7), ) 

response = model.generate_content(prompt) print(f"Run {run}: {response.text.strip()}") print() 

Did it answer confidently? Did it give the same name each run? Did it ever say it didn't know? 

## **Exercise 9 — Expose the arithmetic weakness** 

Write a script that sends arithmetic problems to the model and checks whether the answers are correct. 

import os import google.generativeai as genai from dotenv import load_dotenv 

load_dotenv() genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

model = genai.GenerativeModel( "gemini-1.5-flash", generation_config=genai.types.GenerationConfig(temperature=0), ) 

problems = [ ("17 * 38",   17 * 38), ("127 + 486", 127 + 486), ("1024 / 16", 1024 / 16), ("333 * 27",  333 * 27), ("99999 + 1", 99999 + 1), ] 

print(f"{'Problem':<20} {'Expected':>10} {'Model said':>15} {'OK?':>6}") print("-" * 55) 

for expression, expected in problems: prompt = f"What is {expression}? Reply with only the number, nothing else." response = model.generate_content(prompt) model_answer = response.text.strip() 

try: correct = abs(float(model_answer) - float(expected)) < 0.01 except ValueError: correct = False 

print(f"{expression:<20} {expected:>10} {model_answer:>15} {'✓' if correct else '✗':>6}") 

Which ones did it get right? Which did it get wrong? What pattern do you notice? 

## **Exercise 10 — Give it an escape hatch** 

The way you ask a question changes whether the model admits uncertainty or just makes something up. Compare these two versions. 

import os 

import google.generativeai as genai from dotenv import load_dotenv 

load_dotenv() 

genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

model = genai.GenerativeModel("gemini-1.5-flash") 

# No escape — pressure to answer prompt_a = "What was the exact population of Lahore in 1923?" 

# Escape hatch — permission to be uncertain 

prompt_b = ( 

"What was the exact population of Lahore in 1923? " 

- "If you are not certain, say so and explain what you do know." 

) 

print("--- No escape hatch ---") print(model.generate_content(prompt_a).text.strip()) 

print("\n--- With escape hatch ---") 

print(model.generate_content(prompt_b).text.strip()) 

How different are the two responses? What does this tell you about how to write prompts when accuracy matters? 

## **Check Your Understanding** 

Before moving to Day 4, make sure you can answer these without looking: 

1. Why does a longer conversation eventually cause the model to "forget" earlier messages? 

2. What does temperature = 0 mean in practice? When would you use it? 

3. Why does an LLM give a confident-sounding wrong answer instead of just saying "I don't know"? 

4. You're building a tool to extract order numbers from emails. What temperature would you use and why? 

5. A model's training cutoff is early 2024. A user asks about a news event from late 2024. What's likely to happen? 

## **What This Unlocks** 

Everything from here on — prompt engineering, multi-turn chat, RAG, agents — depends on these fundamentals. When a prompt doesn't work, you'll debug it better because you know the model is predicting tokens, not "thinking." When a model confidently hallucinates, you won't be surprised — you'll know exactly why and how to defend against it. 

