

## Day 14 — Deployment
Your app has been running on your laptop this whole time. Today it goes on the
internet, where anyone with a link can use it.
What you're bringing in: the Document Q&A app with safety guardrails (Days 11–12). Today
doesn't add new AI capability — it makes everything you've already built reachable by
anyone, not just you.
- Putting an App Online — The Options
Why this matters
A project sitting on your laptop is invisible to everyone but you. The same project on a public
URL is something you can put in a portfolio, share in a job application, or hand to a friend to
try. Deployment is the difference between "I built something" and "here, try it."
The two free options
Streamlit Community Cloud — the natural choice if you've built your app in Streamlit (which
you have). Connects directly to a GitHub repo, redeploys automatically when you push
changes, free for public apps.
Hugging Face Spaces — also free, supports Streamlit and Gradio apps, and is well known in
the AI community specifically — useful if you want your portfolio to be discovered by people
already looking at AI projects.
For this course, use Streamlit Community Cloud — it's the most direct path from what
you've already built to a live URL, with the least friction.
What deployment actually requires
Three things, all of which you should already have from Day 14's repo cleanup:
- A public GitHub repo with your app code
- A requirements.txt listing every dependency
## 1 / 8

- A way to provide your API key to the deployed app without it being in the code
The third point is the part most people get wrong the first time. Locally, your key lives in
.env, which is never committed. In the cloud, there is no .env file unless you put it there
— and you must never put it there. Instead, the hosting platform gives you a secrets
manager.
Exercise 1 — Pre-deployment checklist
Before touching Streamlit Cloud, verify these on your Document Q&A repo:
requirements.txt exists and lists every package your app imports (streamlit,
google-generativeai, python-dotenv, chromadb, sentence-transformers)
.env is in .gitignore and is confirmed absent from the repo
(git ls-files | grep env should show nothing or only .env.example)
The app runs locally with no errors right now, from a fresh git clone if possible
Your GitHub repo is set to Public — private repos need extra configuration to deploy
Expected output:
If any of these fail, fix them before continuing — a broken checklist item here means a
broken deployment later, just harder to debug because you can't see the cloud server's
filesystem.
$ cat requirements.txt
streamlit
google-generativeai
python-dotenv
chromadb
sentence-transformers
$ git ls-files | grep env
## .env.example
$ streamlit runapp.py
You can now view your Streamlit appin your browser.
Local URL: http://localhost:8501
## 2 / 8

- Environment Variables and Secrets in the Cloud
How Streamlit Cloud handles secrets
Streamlit Cloud has a built-in secrets manager, separate from your code and separate from
your repo. You type your secrets into a text box in the Streamlit Cloud dashboard, and they
become available to your deployed app through st.secrets.
The format mirrors a .env file but uses TOML syntax:
Reading secrets in your code
Your code currently does this for local development:
On Streamlit Cloud, secrets are available through st.secrets instead of environment
variables. The cleanest approach is to support both, so the same code works locally and in
the cloud:
This tries the local .env first, and falls back to Streamlit's secrets manager if that's empty
— which is exactly the case when running in the cloud.
GEMINI_API_KEY = "your_key_here"
## TOML
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
## PYTHON
import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
## PYTHON
## 3 / 8

Exercise 2 — Update your code to support both environments
Modify the load_model() function in your Document Q&A app so it checks both
os.getenv() and st.secrets, in that order. Test it locally first — it should behave exactly
as before, since st.secrets will be empty locally unless you've configured it.
Expected output (running locally, unchanged behaviour):
Don't deploy yet — just confirm the fallback logic doesn't break anything locally before
moving to the actual deployment steps.
Exercise 3 — Deploy to Streamlit Community Cloud
Follow these steps:
- Go to share.streamlit.io and sign in with GitHub
- Click "New app" and select your Document Q&A repository
- Set the main file path to app.py
- Before clicking deploy, open "Advanced settings" and find the secrets box
- Paste in your secret using the TOML format shown above
- Click "Deploy"
The first deploy can take a few minutes — it's installing every package in requirements.txt
from scratch on a fresh server.
Expected output (deployment log, abbreviated):
$ streamlit runapp.py
[App loads normally, using the .env key as before]
[12:03:01]  Python version: 3.11
[12:03:02]  Installing dependencies from requirements.txt//.
[12:04:15] ✅ All packages installed
[12:04:18]  Starting app//.
[12:04:22] ✅ Your app is live at https://yourname-document-qa.streamlit.app
## 4 / 8

Open the URL. Upload a document. Ask a question. If it works exactly as it did locally, you're
done. If it doesn't, the next section covers the most common failure points.
- Debugging a Failed Deployment
The most common failures
"ModuleNotFoundError" — a package your app imports isn't in requirements.txt. Fix: add
the missing package, commit, push. Streamlit Cloud redeploys automatically on every push
to your main branch.
"KeyError: GEMINI_API_KEY" or similar — the secret wasn't set correctly, or your code is
only checking os.getenv() and not falling back to st.secrets. Fix: verify the secrets box
in the Streamlit Cloud dashboard, and check your fallback logic from Exercise 2.
App loads but crashes on file upload or first question — often a version mismatch between
what's installed locally and what's in requirements.txt. Fix: run
pip freeze > requirements.txt locally to capture exact versions, though be aware this can
also pull in unnecessary packages — review the file before committing.
App is extremely slow to start — the embedding model download happens on every cold
start unless cached properly. This is expected behaviour for free-tier hosting; the first
request after a period of inactivity will always be slower.
Exercise 4 — Intentionally break and fix your deployment
This exercise builds real debugging muscle by creating failures in a safe, controlled way.
Break 1 — Remove a dependency
Temporarily delete sentence-transformers from requirements.txt, commit, and push.
Watch the deployment fail. Read the error log Streamlit Cloud shows you. Then add it back,
commit, and push again.
Expected output (after removing the dependency):
## 5 / 8

Break 2 — Clear the secret
In the Streamlit Cloud dashboard, temporarily delete the GEMINI_API_KEY secret. Reload
your app. Observe the error. Then add the secret back.
Expected output (after clearing the secret):
(If you see this exact message instead of a crash, your error handling from Day 4 is working
correctly — even in production.)
Going through both of these deliberately means the first time you see these errors for real,
you'll already know what they mean.
## 4. Basic Logging
Why logging matters once an app is live
When your app runs on your own machine, you see every print statement and every error in
your terminal in real time. Once it's deployed, you're not watching it — but it might fail
anyway, and you need a way to find out what happened after the fact.
Streamlit Cloud keeps a log of your app's console output, viewable from the dashboard. The
simplest improvement you can make today is ensuring your app actually logs useful
information to that console.
What to log
When a document is successfully indexed, and how many chunks
When an API call fails, and what the error was
When a safety guard blocks something (without logging the actual blocked content, to
avoid storing potentially sensitive input)
[12:10:03]  Installing dependencies from requirements.txt.
[12:10:45] ❌ Error running app: ModuleNotFoundError: No module named 'sentence
[App loads but shows]: Error: GEMINI_API_KEY not found in .env
## 6 / 8

Basic usage counts — how many questions have been asked this session
Exercise 5 — Add logging to your deployed app
Add logging calls at these four points in your app:
- After successful document indexing — log the chunk count
- When an API call to Gemini fails — log the error message
- When the injection guard blocks an input — log that a block occurred, not the input itself
- When the app starts — log a simple "App started" message
Push the change, let it redeploy, then use the app for a few minutes — upload a document,
ask a few questions, try one of your injection test prompts from Day 12.
Then check the logs in the Streamlit Cloud dashboard.
Expected output (in the cloud logs):
This is your first real production signal — a record of what your app actually did, separate
from what you assumed it did.
- Catch-Up
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(/_name/_)
logger.info(f"Indexed {chunk_count} chunks from uploaded document")
logger.warning(f"Injection attempt blocked")
logger.error(f"Gemini API call failed: {e}")
## PYTHON
INFO: App started
INFO: Indexed 24 chunks from uploaded document
WARNING: Injection attempt blocked
ERROR: Gemini API call failed: 429 Resource has been exhausted
## 7 / 8

Use any remaining time today to revisit anything from Days 1–13 that didn't fully click, or to
add polish to any of your three projects.
Good candidates for catch-up time:
Re-run your Day 13 eval set against the now-deployed version of your app — does it
perform the same in the cloud as it did locally?
Improve your README with a link to the live deployed app, not just setup instructions
Add the unit converter tool from Day 11 if you skipped the stretch goals
Go back to any "Check Your Understanding" question from a previous day that you
couldn't answer confidently, and revisit that day's material
## Check Your Understanding
Before moving to the Capstone, make sure you can answer these without looking:
- Why can't your deployed app read from a .env file the same way it does locally?
- A teammate's app works locally but fails on Streamlit Cloud with ModuleNotFoundError.
What's the most likely cause?
- Why does the fallback pattern os.getenv(...) or st.secrets.get(...) let the same
code run in both environments?
- Your app's injection guard fires correctly, but you want to know how often without storing
what users actually typed. What should your logging do instead?
- Your app is slow the first time anyone visits after a few hours of no traffic, but fast after
that. Is this a bug?
## 8 / 8