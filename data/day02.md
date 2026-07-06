## **Day 2 — Setup & Your First AI Call** 

API Keys · First LLM Call · Local Models with Ollama 

Duration: 3–4 hrs · Prerequisite: Day 1 complete · Free tier only 

## **What You'll Learn Today** 

- Create free API keys 

   - Google AI Studio (Gemini) 

   - Groq 

   - OpenRouter 

- Install Ollama and pull a local model 

- Make your first LLM call from Python 

- Load secrets safely from a .env file 

- Call a local model from Python 

- Handle errors gracefully with try/except 

## **Research** 

- What is an API? 

- What is HTTP? 

- HTTP Methods (GET, POST, PUT, DELETE) 

- Environment Variables 

## **Exercises** 

## **Exercise 01 — Get Your Free API Keys** 

Sign up for free API keys from Google AI Studio, Groq, and OpenRouter. Install the libraries you'll need for today inside your virtual environment. 

- Go to aistudio.google.com and create a free Gemini API key. 

- Go to groq.com and create a free Groq API key. 

- Go to openrouter.ai and create a free OpenRouter key. 

- Install the google-generativeai and python-dotenv packages inside your venv. 

_Note: Having three providers means you can switch in seconds if one hits a rate limit._ 

_Bonus: Read the free-tier limits for each provider and note which one is most generous._ 

Page 1  ·  AI Engineer 30-Day Roadmap  ·  Day 2 

## **Exercise 02 — Store Your API Key Safely in a .env File** 

Create a .env file to hold your API key, and a .gitignore file to make sure it is never pushed to GitHub. 

- Create a file called .env in your project folder. 

- Add your Gemini key as GEMINI_API_KEY=your_key_here. 

- Create a .gitignore file and add .env on its own line. 

- Confirm both files exist in the project folder. 

_Note: A leaked API key can result in unexpected charges. The .gitignore step is not optional._ 

_Bonus: Look up what happens if you accidentally push a secret to GitHub and how to fix it._ 

## **Exercise 03 — Load and Verify Your Key in Python** 

Write a script that loads your API key from the .env file using python-dotenv, then prints only the first 6 characters to confirm it loaded without exposing the full key. 

- Import os and load_dotenv from the dotenv package. 

- Call load_dotenv() then read the key with os.getenv. 

- Print a message confirming the key loaded, showing only the first 6 characters. 

- Add an else branch that prints a helpful error if the key is missing. 

_Note: Never print the full key — even in a terminal that others might see._ 

_Bonus: Temporarily rename your .env file and run the script again. Observe the error message, then rename it back._ 

## **Exercise 04 — Make Your First LLM Call** 

Write a script that sends one question to the Gemini API and prints the answer. This is your first real interaction with a language model through your own code. 

- Load your API key from .env. 

- Configure the google.generativeai library with the key. 

- Create a model object using gemini-1.5-flash. 

- Send a simple question using generate_content and print the response text. 

_Note: You won't fully understand every line yet — that's fine. By Week 2 you will._ 

_Bonus: After the call, print the usage metadata from the response. It shows the number of tokens used, which is how the API measures cost and limits._ 

## **Exercise 05 — Handle Errors Gracefully** 

Improve your script from Exercise 4 so it never crashes with an ugly traceback. Check for a missing key before making the call, and wrap the API call in a try/except block. 

- Check if the key exists right after loading it. If not, print a clear message and exit. 

- Wrap your generate_content call in a try block. 

- In the except block, print the error message in a readable format. 

- Test it by temporarily using a wrong API key. 

_Note: Good error handling is what separates a script from a real tool._ 

_Bonus: Look up the specific exception that Google's library raises when a quota is exceeded. Add a separate except block just for that case._ 

Page 2  ·  AI Engineer 30-Day Roadmap  ·  Day 2 

## **Exercise 06 — Build an Interactive Question Script** 

Extend your script to take a question from the user at runtime using input(), then send it to Gemini and print the answer. 

- Use input() to prompt the user for a question. 

- Strip whitespace from the input. 

- If the input is empty, print a message and exit cleanly. 

- Otherwise, send it to the API and print the result. 

_Note: Run it and ask at least 3 different questions._ 

_Bonus: Run the same question three times in a row and notice the answer changes slightly each time. This is the model's randomness, called temperature, in action._ 

## **Exercise 07 — Ask Multiple Questions in a Loop** 

Modify your script to keep asking for questions in a loop until the user decides to quit, instead of exiting after a single answer. 

- Wrap your input and API call inside a while True loop. 

- If the user types quit or exit, break out of the loop with a goodbye message. 

- If the input is empty, skip the API call and prompt again. 

- Otherwise, send the question and print the answer, then loop back. 

_Note: Notice that the model does not remember your earlier questions — each call is independent. Day 6 covers how to fix this with conversation history._ 

_Bonus: Count how many questions the user has asked and print the total when they exit._ 

## **Exercise 08 — Install Ollama and Run a Local Model** 

Install Ollama on your machine and download a small local model. Have a conversation with it directly from your terminal — no API key and no internet connection needed. 

- Download and install Ollama from ollama.com for your operating system. 

- Open a new terminal window and pull the gemma2:2b model (about 1.6 GB). 

- Start a chat session with the model directly in the terminal. 

- Ask it a question and then exit the session. 

_Note: Ollama runs entirely on your machine — your prompts stay private and there are no usage limits._ 

_Bonus: Ask Ollama the same question you sent to Gemini in Exercise 4. Write down one difference you notice — speed, length, or accuracy._ 

Page 3  ·  AI Engineer 30-Day Roadmap  ·  Day 2 

## **Exercise 09 — Call Ollama from Python** 

Write a Python script that sends a question to your local Ollama model using the requests library. Compare the code structure with your Gemini script. 

- Install the requests library if it is not already in your venv. 

- Write a function that sends a POST request to the local Ollama API endpoint with the model name and prompt. 

- Parse the response JSON and return the answer text. 

- Use input() to ask the user for a question, call your function, and print the answer. 

_Note: Make sure Ollama is running before executing this script. It starts automatically after install on most systems._ 

_Bonus: Ask Ollama the same question three times and see if the answers vary like Gemini's did._ 

## **Exercise 10 — Build a Provider-Switcher Script** 

Combine your Gemini and Ollama scripts into one. Ask the user to choose a provider at the start, then route their question to the right model. This is your Day 2 mini-capstone. 

- Print a menu asking the user to choose between Gemini (cloud) and Ollama (local). 

- Read their choice with input(). 

- Ask for a question, then call either your Gemini function or your Ollama function depending on the choice. 

- Print the answer with a label showing which provider responded. 

_Note: This pattern — swapping providers behind a common interface — is how real AI apps are built to be model-agnostic._ 

_Bonus: Add a third option that sends the same question to both providers and prints both answers side by side for comparison._ 

## **Day 2 Summary** 

01. Get Your Free API Keys — Gemini, Groq, OpenRouter setup 

02. Store Key Safely in .env — Secret management 

03. Load and Verify the Key — python-dotenv 

04. Make Your First LLM Call — Gemini API — the magic moment 

05. Handle Errors Gracefully — try / except / sys.exit 

06. Interactive Question Script — input() + API integration 

07. Ask Multiple Questions in a Loop — while loop + flow control 

08. Install Ollama Locally — Local LLMs — no quota 

09. Call Ollama from Python — requests library 

10. Build a Provider-Switcher Script — Model-agnostic design 

Next up — Day 3: Files, Errors & Secrets — reading JSON files, writing output, and handling bad input gracefully. 

Page 4  ·  AI Engineer 30-Day Roadmap  ·  Day 2 

