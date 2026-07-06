

## Day 15 — Capstone Day 1: Plan & Design
Everything from the last two weeks has been building toward this. Today you decide
what your capstone is and design it properly before writing a single line of code.
What you're bringing in: every project so far — the CLI chatbot (Day 4), RAG with citations
(Days 7–8), the Streamlit interface (Day 9), the agent (Days 10–11), safety guardrails (Day 12),
evaluation (Day 13), and deployment (Day 14). The capstone combines what you choose
from these into one cohesive project, deployed and polished.
There is no code today. Today is entirely about deciding and designing — the highest-
leverage hour you can spend on a project is the one before you start building, and it's the
hour most people skip.
## 1. Choosing Your Capstone
The three options
A chatbot — a conversational assistant with a clear persona, multi-turn memory, and a
specific purpose. Lowest technical complexity of the three, but the bar for a good chatbot
project is having a genuinely useful, specific purpose rather than a generic "ask me
anything" bot.
A RAG app — document or knowledge-base question answering, like your Day 11 project but
built around a new domain or document set that's meaningfully different from the course
exercises. The strongest path if you want to show depth in the RAG pipeline: chunking
strategy, retrieval quality, citations, and evaluation.
A simple agent — a tool-using agent like Day 10–11, but solving a real problem with real tools
(not the simulated search). The most technically impressive of the three if done well, but also
the easiest to overscope — agents have more moving parts and more failure modes.
How to actually choose
Don't pick based on which sounds most impressive. Pick based on:
## 1 / 7

- A real use case you actually care about. A capstone you're motivated to finish beats a
more ambitious one you lose interest in by Day 17.
- What you can realistically finish in 4 days, including the polish and deployment days.
Better to ship a focused, polished RAG app than an ambitious half-working agent.
- What demonstrates the skills you most want to show a future employer. If you're
targeting roles that need RAG and document processing, build a RAG app. If you want to
show agentic reasoning, build the agent.
Exercise 1 — Decide and justify
Write down, in a few sentences each:
Which of the three options you're choosing
One real, specific use case for it (not "a chatbot that answers questions" — something
like "a chatbot for new interns at Techgebra that answers questions about our onboarding
process and internal tools")
Why you're choosing this over the other two
There's no single right answer here — the point is making a deliberate choice you can
commit to for four days, instead of drifting between ideas.
Expected output (example, not a requirement to copy):
- Writing a One-Page Spec
Capstone choice: RAG app
Use case: A Q&A tool for the AI Engineering Internship cohort that answers
questions about course material — interns can ask "what did we cover on
chunking?" insteadof searching through 13 markdown files.
Why this over the others: I already have strong RAG fundamentals from
Days 7–8and want to go deeper on retrieval quality and evaluation rather
than start something new. The use caseisreal — I'd actually use this.
## 2 / 7

Why a spec matters
A spec forces you to think through the project before code makes the decisions for you.
Without one, scope creeps day by day — "while I'm in here, let me also add..." — and
capstones routinely end up unfinished because of this. A clear spec, written and committed
to before building, is the single best defence against that.
What goes in it
A good one-page spec answers four questions, each in a short paragraph:
What does it do? A clear, specific description of the core functionality. Not a feature list — a
description of the actual user experience.
Who is it for? A specific person or role, even if that's just "me" or "interns at my company."
Specificity here forces clarity everywhere else.
How does it work? A plain-English walkthrough of the pipeline — what happens from the
moment a user interacts with it to the moment they get a result.
What's explicitly out of scope? Just as important as what's in scope. Naming what you're
not building prevents you from accidentally trying to build it on Day 17 when you're under
time pressure.
Exercise 2 — Write your spec
Using the structure above, write your one-page spec. Keep each section to 3–5 sentences —
the goal is clarity, not length.
Expected structure (using the example use case from Exercise 1):
# Capstone Spec — Internship Course Q&A
## What it does
A web app where AI Engineering interns can ask natural-language questions
about course material and get answers grounded in the actual lesson content,
with citations pointing to which day's material the answer came from.
## Who it's for
Interns in the Techgebra AI Engineering Internship cohort who want a faster
way to find information than searching through 13+ markdown files manually.
## MARKDOWN
## 3 / 7

Write your own version of this for your chosen capstone. Save it as SPEC.md — you'll add it
to your repo later today.
- Sketching the Architecture
Why sketch before building
A spec describes what the app does. An architecture sketch describes how the pieces fit
together — which is a different kind of thinking, and skipping it is how projects end up with
tangled, hard-to-debug code.
You don't need fancy diagramming tools. A sketch on paper, in a notes app, or in a simple
text-based diagram is enough. What matters is that you've thought through the pieces and
the connections between them before writing code.
What to include
The main components — UI, embedding model, vector store, LLM, any tools
The data flow — what happens first, second, third, in order
External dependencies — which APIs or services you're relying on, and what happens if
they're slow or fail
Where state lives — what's stored where (in memory, on disk, in the vector database)
## How it works
- All daily lesson markdown files are loaded and chunked
- Chunks are embedded and stored in a persistent Chroma collection,
tagged with metadata indicating which day they came from
- A user types a question into a Streamlit interface
- The question is embedded and matched against the closest chunks
- Gemini generates an answer using only the retrieved context
- The answer is shown with citations indicating which day(s) it drew from
## Out of scope
- No support for file formats other than markdown
- No user accounts or saved conversation history
- No editing of lesson content through the app
- Not optimised for documents outside the course material domain
## 4 / 7

Exercise 3 — Draw your architecture
Sketch your capstone's architecture. A simple text-based version works fine if you don't
have diagramming tools:
Expected output (example, using the same use case):
If your capstone is an agent instead of a RAG app, your sketch should show the ReAct loop
instead — the model, the tools, and how control passes between them.
- Setting Up the Repo
What "set up" means today
You're not writing application code yet. You're creating the skeleton: the repo, the file
structure, the README outline, and the .gitignore — all the scaffolding so that tomorrow
you can start writing the actual pipeline without any setup friction.
[User]
↓ types question in Streamlit UI
[Streamlit App]
↓ embeds question
[Sentence Transformers model] (cached, loaded once)
↓ query embedding
[Chroma persistent collection] (pre-indexed from 13 markdown files)
↓ top3 chunks + metadata (day number)
[Streamlit App]
↓ builds prompt with context + question
[Gemini API] (system prompt: answer only from context, cite the day)
↓ answer text
[Streamlit App]
↓ displays answer + sources, grouped by day
Indexing pipeline (runs once, separately):
[13 markdown files] → [chunker] → [embedder] → [Chroma collection on disk]
## 5 / 7

Exercise 4 — Initialise the capstone repo
Create a new repo with this structure:
Your .gitignore should be the same standardised one from earlier in the course — .env,
__pycache__/, chroma_db/, and so on.
Write a skeleton README.md — not the full polished version (that comes on the polish day),
just enough to mark out the sections you'll fill in:
Commit your SPEC.md, your skeleton README.md, and your .gitignore:
Expected output:
capstone/
## ├── .env
## ├── .gitignore
├── requirements.txt
├── SPEC.md
├── README.md
├── app.py
└── data/              ← your source documents, if applicable
# [Your Capstone Name]
[One-sentence description — fill in properly later]
## ## Status
 In progress — Capstone project, Day 1 of 4
## How it works
[Coming soon]
## ## Setup
[Coming soon]
## MARKDOWN
git init
git add .
git commit -m "Initialise capstone repo with spec and README skeleton"
## BASH
## 6 / 7

## 5. Final Check Before Tomorrow
Before ending today, re-read your SPEC.md once more and ask yourself honestly:
Can I realistically build this core pipeline in one day (Day 16)?
Can I realistically add a usable interface in one day (Day 17)?
Is there anything in my "what it does" section that's actually more ambitious than it needs
to be?
If the answer to the third question is yes, trim it now. It is far easier to cut scope today, on
paper, than on Day 17 when you're debugging a UI and discover the underlying pipeline was
too ambitious to finish properly.
## Check Your Understanding
Before moving to Capstone Day 2, make sure you can answer these without looking:
- Why is writing a spec before coding considered higher leverage than the same hour
spent writing code?
- What's the difference between what goes in your spec's "how it works" section and what
goes in your architecture sketch?
- Why does a spec need an explicit "out of scope" section?
- Your architecture sketch shows the embedding model being loaded fresh on every user
question. Is that a problem? What would you check from Day 9?
- You're tempted to add "and it should also support PDF uploads" to your spec right now.
What should you do with that idea instead of adding it immediately?
$ git log --oneline
a1b2c3d Initialise capstone repo with spec and README skeleton
$ ls
.env.gitignore  README.md  SPEC.md  app.py  data  requirements.txt
## 7 / 7