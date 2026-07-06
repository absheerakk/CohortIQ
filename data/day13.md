

Day 13 — Evaluating AI
You've been checking your app by reading the output and deciding "that looks right."
Today you make that process systematic.
What you're bringing in: your Document Q&A app (Day 11), prompt engineering (Day 4), and
your understanding of why models hallucinate (Day 3). Evaluation is applied prompt
engineering — you're using the model to assess the model.
- Why Testing LLMs Is Hard
The problem with traditional testing
In regular software, you test by asserting that a function returns exactly the expected value.
Given the same input, the function always returns the same output. A test either passes or
fails — no ambiguity.
LLMs break all of this:
The same prompt can produce different outputs at temperature > 0
"Correct" is often a matter of degree, not true/false — an answer can be partially right,
mostly right, or right but poorly phrased
There is rarely a single ground-truth answer to compare against
The output is natural language — you can't assertEqual a paragraph
What evaluation looks like instead
Instead of pass/fail unit tests, LLM evaluation uses scoring on dimensions:
Correctness — is the factual content right?
Faithfulness — is the answer grounded in the source document, or did the model invent
things?
Relevance — does the answer actually address the question asked?
Completeness — does it cover everything the question asked for?
## 1 / 10

You score each response on each dimension, usually on a scale of 1–5. Average the scores
across a set of test questions to get a sense of how well the system is performing.
What an eval set is
An evaluation set (eval set) is a collection of test cases you've prepared in advance:
Each case has a question, an expected answer, and the source context it should be drawn
from. You run your app on each question, collect the actual answers, and then score them.
Exercise 1 — Build your eval set
Create a file called eval_set.json containing 10 question/expected-answer pairs for the
Python facts document used in Days 7–8. Cover a range of difficulty:
3 straightforward factual questions (single sentence answer)
3 questions requiring combining two pieces of information
2 questions where the answer is in the document but not obvious
2 questions where the answer is not in the document (expected answer: "I don't have
that information")
Expected structure:
## [
## {
"question":"When was Python created?",
"expected":"Python was first released in 1991 by Guido van Rossum.",
"context":"Python was created by Guido van Rossum and first released in 19
## },
## ...
## ]
## JSON
## [
## {
"question":"Who created Python?",
"expected":"Python was created by Guido van Rossum.",
## "in_document":true
## },
## {
## JSON
## 2 / 10

Write all 10 by hand — don't generate them with the model. The point is that you decide what
correct looks like before running any tests.
Exercise 2 — Run your app against the eval set
Write a script that:
- Loads eval_set.json
- Loads and indexes the Python facts document (the same one from Days 7–8)
- Runs each question through the RAG pipeline
- Saves the actual answers alongside the expected answers to eval_results.json
Expected structure of eval_results.json:
Print a summary after running:
Expected output:
"question":"What is the population of France?",
"expected":"I don't have that information.",
## "in_document":false
## }
## ]
## [
## {
"question":"Who created Python?",
"expected":"Python was created by Guido van Rossum.",
"actual":"Python was created by Guido van Rossum and first released in 199
## "in_document":true
## }
## ]
## JSON
Running eval set (10 questions)...
[1/10] Who created Python?              ✓ answered
[2/10] What is Python used for?         ✓ answered
[3/10] What happened to Python 2?       ✓ answered
## ...
[9/10] What is the population of France? ✓ answered
## 3 / 10

Note: "✓ answered" just means the app returned a non-empty response — not that it's
correct. Scoring comes in the next section.
- LLM-as-Judge
The idea
Once you have actual answers alongside expected answers, someone needs to decide how
well the actual answer matches the expected one. You could read each one yourself — but
at 10 questions that's manageable, at 1,000 it isn't.
LLM-as-judge uses a second model call to score each answer. You send the question, the
expected answer, and the actual answer to the model, and ask it to return a score and a
reason.
This is the dominant approach in production AI evaluation. It scales, it's consistent (the same
judge prompt applied to all answers), and it correlates well with human judgement for most
tasks.
The judge prompt
The judge prompt is critical — it determines what "good" means. A vague judge prompt
produces vague, inconsistent scores. A specific judge prompt with a clear rubric produces
reliable scores you can act on.
A good judge prompt:
Defines each score level concretely
Asks for a reason before the score (chain-of-thought improves accuracy)
Asks for a structured output you can parse (JSON works well)
Separates dimensions — one score for correctness, one for faithfulness
[10/10] Who is the current president?    ✓ answered
Done. Results saved to eval_results.json.
## 4 / 10

Exercise 3 — Write the judge prompt
Write a system prompt for a judge model that scores RAG answers on two dimensions:
Correctness — does the actual answer convey the same information as the expected
answer?
5: completely correct, all key facts match
3: partially correct, some key facts right but something missing or wrong
1: incorrect or completely missing the point
Faithfulness — is the actual answer grounded in the provided context, or does it add
information from outside?
5: everything in the answer comes directly from the context
3: mostly grounded, but one or two details seem added from outside
1: the answer contradicts the context or invents facts
The prompt should ask the model to return JSON in this format:
Write the full system prompt. Print it and read it carefully — it is the definition of "quality" for
your app.
Exercise 4 — Score one result manually with the judge
Before running the judge across all 10 results, test it on a single case to make sure it's
working as expected.
Take the first result from eval_results.json and send it to the judge model with this user
prompt structure:
## {
## "correctness_score":4,
"correctness_reason":"The answer correctly identifies the creator and year b
## "faithfulness_score":5,
"faithfulness_reason":"All information in the answer appears in the provided
## }
## JSON
## 5 / 10

Parse the JSON response and print the scores and reasons.
Expected output:
If the judge gives an unexpected score, look at the reason — is it interpreting your rubric
correctly? Adjust the judge prompt until it gives consistent, sensible scores on this first case
before running the full set.
Exercise 5 — Run the judge across all 10 results
Write a script that loops over every result in eval_results.json, sends each one to the
judge, parses the scores, and saves everything to eval_scores.json.
Expected structure of eval_scores.json:
## Question: {question}
Expected answer: {expected}
Actual answer: {actual}
Context used (retrieved chunks):
## {context}
Score the actual answer on correctness and faithfulness.
Question: Who created Python?
Expected: Python was created by Guido van Rossum.
Actual:   Python was created by Guido van Rossum and first released in1991.
## Correctness:5/5
Reason: The answer correctly identifies the creator. The additional year detail
is accurate and consistent with the expected answer.
## Faithfulness:5/5
Reason: Both facts (creator name and year) appear directly in the provided cont
## [
## {
## JSON
## 6 / 10

After saving, print a summary:
Expected output:
Look at your scores. Which questions did worst? Do the reasons explain why? Are there
patterns — does a certain type of question (multi-fact, out-of-document) consistently score
lower?
- Fine-tuning vs RAG vs Prompting
When each approach makes sense
These three approaches all improve LLM output quality, but in completely different ways and
at completely different costs.
Prompting — changing what you put in the prompt.
Cost: zero
"question":"Who created Python?",
"expected":"Python was created by Guido van Rossum.",
"actual":"Python was created by Guido van Rossum and first released in 199
## "correctness_score":5,
## "correctness_reason":"...",
## "faithfulness_score":5,
## "faithfulness_reason":"..."
## }
## ]
Eval complete. Results:
Q1:  Correctness 5/5  |  Faithfulness 5/5  |  Who created Python?
Q2:  Correctness 4/5  |  Faithfulness 5/5  |  What is Python used for?
Q3:  Correctness 5/5  |  Faithfulness 5/5  |  What happened to Python 2?
## ...
Q9:  Correctness 5/5  |  Faithfulness 5/5  |  What is the population of Franc
Q10: Correctness 5/5  |  Faithfulness 5/5  |  Who is the current president?
Average correctness:4.6/5.0
Average faithfulness:4.9/5.0
## 7 / 10

Time: minutes
When to use: first always. Most problems that look like model capability problems are
actually prompt problems. Better examples, clearer instructions, chain-of-thought — try
these before anything else.
Limits: can't teach the model facts it doesn't know, and has diminishing returns once the
prompt is well-crafted
RAG — giving the model relevant documents at query time.
Cost: embedding + vector DB storage (cheap to free)
Time: hours to set up, seconds per query
When to use: when the model needs access to specific knowledge it wasn't trained on —
your company's documents, recent events, proprietary data. This is what you've built
across Days 5–11.
Limits: only works for knowledge that can be retrieved from documents. Doesn't help if
the model's reasoning is weak.
Fine-tuning — retraining the model weights on your specific data.
Cost: high (GPU hours, often $$$)
Time: days to weeks for training, plus labelled data collection
When to use: rarely, and only after prompting and RAG have been tried. Use it when you
need the model to adopt a very specific style or tone consistently, or when you're doing
the same task millions of times and need maximum efficiency
Limits: expensive, requires labelled data, and can cause the model to forget general
capabilities (catastrophic forgetting)
The decision tree
Problem: model gives wrong or low-quality answers
## ↓
Step1: Is this a prompt problem?
→ Try better instructions, examples, chain-of-thought
## → Fixed? Done.
## ↓
Step2: Does the model lack the knowledge to answer?
→ Build RAG — give it the documents
## → Fixed? Done.
## 8 / 10

In practice, 90% of problems are solved at Step 1 or Step 2. Fine-tuning is rarely the right
answer for projects at this stage.
Exercise 6 — Diagnose your eval results
Go back to your eval_scores.json. For each question that scored below 4 on either
dimension, diagnose the failure:
Write down for each low-scoring result:
Was the retrieved context actually relevant? (retrieval failure)
Was the context relevant but the answer wrong anyway? (generation failure)
Was the answer correct but phrased differently from expected, causing the judge to
score low? (judge calibration issue)
Was the question genuinely unanswerable from the document? (expected behaviour)
Then for each retrieval failure, decide: would a better chunking strategy fix it, or does the
document not contain the answer?
For each generation failure, decide: would a better system prompt fix it, or is this a model
capability limit?
Expected output (written analysis, not code):
## ↓
Step3: Is the style or format consistently wrong despite good prompts?
→ Consider fine-tuning. Budget and data ready?
→ Yes: fine-tune. No: go back toStep1and iterate.
Q4 — "What paradigms does Python support?" — Correctness: 2/5
Retrieved context: "Python's design philosophy emphasises readability..."
Issue: retrieval failure — the chunk about paradigms wasn't retrieved.
Fix: overlapping chunks should catch this. Try increasing top_k to5.
Q7 — "What replaced Python 2?" — Correctness: 3/5
Retrieved context: correct chunk was retrieved.
Issue: generation failure — model said "Python 3 replaced it" but didn't
mention the 2020end-of-life date the expected answer included.
Fix: prompt the model to include all details from the context, not just the m
## 9 / 10

This is the core skill of AI engineering: not just building the pipeline, but understanding why it
fails and knowing which lever to pull.
## Check Your Understanding
Before moving to Day 14, make sure you can answer these without looking:
- Why can't you use a simple assertEqual to test LLM output the way you test regular
code?
- What is the difference between a correctness failure and a faithfulness failure in a RAG
system?
- You run your eval set and 8 out of 10 questions score 5/5. The other 2 both involve multi-
sentence answers. What might be causing the lower scores?
- A teammate says you should fine-tune the model because the answers aren't quite in the
right tone. What would you suggest trying first, and why?
- Your judge model gives a score of 2/5 for an answer that looks correct to you when you
read it. What are two possible explanations?
## 10 / 10