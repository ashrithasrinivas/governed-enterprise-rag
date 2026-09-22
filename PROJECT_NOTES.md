# Governed RAG Project — Study & Review Notes

These notes are my personal reference for understanding the Governed Enterprise Policy RAG project, including how the RAG pipeline works, where governance controls are applied, what problems were discovered during testing, and what I learned from the project.

---

# 1. What Did I Build?

I built a small Retrieval-Augmented Generation (RAG) application using fictional enterprise policy documents from a fictional company called Acme Financial Services.

The application allows a user to ask questions such as:

- How much PTO can I carry over?
- How many days per week can I work remotely?
- What was the PTO carryover rule in 2025?
- What does the Health Insurance Policy say about coverage?

Instead of allowing the language model to answer only from its general knowledge, the application retrieves relevant information from the enterprise policy documents and provides that information to the LLM as context.

The project goes beyond basic RAG by adding enterprise data-governance controls.

The system considers:

- Which document is authoritative?
- Is the document approved or retired?
- Which version was valid at the time being asked about?
- Who owns the document?
- What is its classification?
- Is the user authorized to access it?
- Can the answer be traced back to its source?
- Is the generated answer actually supported by retrieved information?
- What should happen when the available documents cannot answer the question?

The main purpose of the project was therefore not simply:

> "Can I build a chatbot?"

The more important question was:

> "How would the data-governance principles I already know need to operate inside a RAG application?"

---

# 2. The Big Picture

The project follows this general flow:

Policy PDFs  
↓  
Extract text  
↓  
Attach governance metadata  
↓  
Split documents into chunks  
↓  
Convert chunks into embeddings  
↓  
Store embeddings and metadata in ChromaDB  
↓  
User asks a question  
↓  
Apply governance/access filters  
↓  
Perform semantic retrieval  
↓  
Apply version and temporal controls  
↓  
Provide governed context to the LLM  
↓  
Generate the answer  
↓  
Add source attribution from metadata  
↓  
Evaluate the result

A simple way to remember this is:

**Govern the source → prepare the data → retrieve the right evidence → control what reaches the LLM → validate the answer.**

---

# 3. Why RAG Was Needed

A language model has general knowledge, but it does not automatically know which internal enterprise document is the approved source for a specific business question.

For example, the model should not decide on its own whether PTO Policy Version 2.0 or Version 3.0 is authoritative.

RAG allows the application to retrieve information from enterprise-controlled sources and provide that information to the LLM at question time.

In this project:

**LLM = generates the natural-language response**

**RAG = supplies relevant enterprise information to the LLM**

**Governance = determines what information is valid, authoritative and permitted to reach the LLM**

This distinction is one of the most important concepts from the project.


# 4. How Documents Become Searchable in RAG

## Step 1 — Start With Source Documents

The source data for this project is a set of fictional enterprise policy PDFs.

Examples include:

- PTO Policy
- Remote Work Policy
- Parental Leave Policy
- Health Insurance Policy
- Travel & Expense Policy
- Employee Handbook

The PDF itself is the source document, but a vector database cannot simply reason over a PDF file directly.

The document first needs to be processed.

---

## Step 2 — Extract the Text

PyPDF is used to extract text from the policy PDFs.

Conceptually:

PDF → Extracted text

For example, a PTO PDF may contain:

"Employees may carry over up to 10 unused PTO days into the following calendar year."

Once extracted, the text can be processed by the RAG pipeline.

---

## Step 3 — Attach Governance Metadata

The project has a document catalog containing information such as:

- Document ID
- Document name
- Business owner
- Classification
- Version
- Status
- Effective date
- Expiration date
- Source system
- Access group

Example:

PTO Policy  
Document ID: HR-PTO-001  
Version: 3.0  
Status: Approved  
Owner: Human Resources  
Access Group: All Employees

This metadata is important because semantic similarity alone cannot determine whether a document is approved, current, restricted, or authoritative.

---

## Step 4 — Split Documents Into Chunks

Large documents are divided into smaller pieces called chunks.

In this project I used approximately:

Chunk size = 700 characters  
Chunk overlap = 100 characters

Conceptually:

Document

↓

Chunk 1  
Chunk 2  
Chunk 3  
Chunk 4

Why chunk?

When someone asks about PTO carryover, the system does not need to send an entire employee policy document to the LLM.

It should retrieve the smaller section containing the relevant information.

Overlap helps preserve context when a sentence or idea falls near the boundary between two chunks.

---

# 5. Embeddings

An embedding converts text into a numerical representation of its semantic meaning.

In this project I used:

`all-MiniLM-L6-v2`

The model converts each chunk into a vector containing 384 dimensions.

Conceptually:

"Employees can carry over 10 unused PTO days."

↓

Embedding model

↓

[0.12, -0.34, 0.08, ... many more numbers]

The individual numbers are not meaningful to a business user.

Together, however, the vector represents characteristics of the text's meaning.

This allows the system to compare the meaning of different pieces of text mathematically.

---

## Embeddings vs. Metadata

This distinction is extremely important.

**Embeddings help answer:**

"What content is semantically similar to this question?"

**Metadata helps answer:**

"Is this the right document to use?"

For example, both PTO Version 2.0 and PTO Version 3.0 may be semantically similar to:

"How much PTO can I carry over?"

Embeddings may retrieve both.

Governance metadata tells the application:

Version 2.0 = Retired  
Version 3.0 = Approved

Therefore, embeddings do not replace metadata.

For enterprise RAG, they serve different purposes.

---

# 6. Vector Database — ChromaDB

The embeddings are stored in ChromaDB.

ChromaDB acts as the vector database for this prototype.

Each stored chunk includes:

- The chunk text
- Its embedding
- Its governance metadata

Conceptually:

Chunk

+

Embedding

+

Metadata

↓

ChromaDB

The Chroma collection used in the project is:

`acme_policy_chunks`

The prototype contains chunks from both Approved and Retired policies because historical questions may legitimately require a retired policy.

---

# 7. What Happens When a User Asks a Question?

Suppose the user asks:

"How much vacation can I roll over to next year?"

The question itself is converted into an embedding using the same embedding model.

Question

↓

Question embedding

↓

Compare against stored chunk embeddings

↓

Find semantically similar chunks

This is semantic retrieval.

The system is looking for content with similar meaning, not simply matching identical words.

For example:

"vacation rollover"

can still retrieve content discussing:

"PTO carryover"

even though the wording is different.

This is one of the major advantages of embedding-based retrieval over simple keyword matching.

---

# 8. The Key Governance Lesson

Semantic similarity does not mean that a document is authoritative.

A chunk can be highly relevant to the question but still be:

- Retired
- Outdated
- Restricted
- From the wrong policy
- Valid for a different time period

Therefore:

**Semantic retrieval answers "What looks relevant?"**

**Governance answers "What am I actually allowed to trust and use?"**

The RAG system needs both.


# 9. Where Governance Enters the RAG Pipeline

A basic RAG system might follow:

Question → Semantic Retrieval → LLM → Answer

My prototype adds governance controls around retrieval:

Question  
↓  
Identify user access  
↓  
Determine whether the question is current or historical  
↓  
Apply metadata/access filters  
↓  
Semantic retrieval  
↓  
Apply temporal/version rules  
↓  
Validate requested policy  
↓  
Build governed context  
↓  
LLM  
↓  
Apply response and citation controls  
↓  
Answer

The important principle is:

**The LLM should receive only information that has already passed the appropriate governance controls.**

---

# 10. Current vs. Historical Policy Governance

The project intentionally contains two versions of the PTO Policy.

### PTO Version 2.0

- Status: Retired
- Effective: 2025-01-01
- Expiration: 2025-12-31
- Carryover: 5 unused PTO days

### PTO Version 3.0

- Status: Approved
- Effective: 2026-01-01
- Carryover: 10 unused PTO days

Both versions discuss the same subject, so their chunks can both be semantically relevant to a PTO question.

However, they are not equally authoritative for every question.

For a current question such as:

"How much vacation can I roll over to next year?"

the application restricts eligible documents to Approved policies.

Therefore Version 3.0 is used.

For a historical question such as:

"How many PTO days could employees carry over in 2025?"

the application detects the year and allows policies that were valid during that historical period.

Therefore Version 2.0 becomes the appropriate source.

This demonstrates an important distinction:

**Retired does not necessarily mean unusable.**

A retired document may still be the authoritative source when answering a historical question.

---

# 11. Access Control

The Health Insurance Policy was intentionally configured as restricted content.

Its metadata includes:

Classification: Confidential - Employee Benefits  
Access Group: Benefits

For this prototype:

An All Employees user can retrieve documents available to All Employees.

A Benefits user can retrieve All Employees documents plus Benefits-restricted documents.

The important design principle is that authorization happens before restricted content is supplied to the LLM.

Correct pattern:

User  
↓  
Authorization / access filtering  
↓  
Eligible documents  
↓  
Retrieval  
↓  
Safe context  
↓  
LLM

An unsafe pattern would be:

Retrieve everything  
↓  
Send restricted content to LLM  
↓  
Ask the LLM not to reveal it

The second approach is weaker because unauthorized information has already entered the model context.

**Security should not depend only on the LLM following instructions.**

---

# 12. Requested-Policy Validation

During testing I discovered another subtle problem.

Suppose an unauthorized employee asks:

"What does the Health Insurance Policy say about employee coverage?"

Access control correctly removes the Health Insurance Policy.

However, semantic retrieval may still find another policy such as the Benefits Eligibility Guide because it discusses a similar topic.

Without an additional control, the system could answer the Health Insurance question using a different policy.

That would mean:

**Security worked, but answer governance failed.**

To address this, the application checks whether the user explicitly requested a known policy.

If the requested policy is not present in the authorized, filtered retrieval results, the application stops before calling the LLM and returns an insufficient-information response.

This prevents an unrelated policy from being substituted as the authoritative source.

---

# 13. Unsupported Questions

Another test asks:

"What is the company's 2027 employee bonus percentage?"

The fictional policy corpus does not contain this information.

A RAG system should not answer simply because the vector database can always return the "closest" chunks.

The closest chunk is not necessarily a valid source.

For this small prototype, unsupported bonus questions are intercepted using a simple deterministic topic check.

The system returns:

"The available policy documents do not contain enough information to answer this question."

No source citation is attached.

This is intentionally a prototype-level control.

A production implementation would require a more scalable approach such as retrieval-confidence rules, corpus coverage metadata, routing, policy taxonomy, or other validation mechanisms rather than a hard-coded topic list.

---

# 14. Why Some Controls Are Deterministic

One of the biggest lessons from the project was that important governance behavior should not depend entirely on prompting the LLM.

For example, I do not want to rely only on a prompt saying:

"Please do not expose restricted information."

or:

"Please cite the correct policy version."

Where possible, important controls are implemented in application logic and metadata.

Examples include:

- Access filtering
- Approved vs. Retired status filtering
- Effective-date filtering
- Requested-policy validation
- Unsupported-question handling
- Source attribution

The LLM is primarily responsible for generating the natural-language answer from the governed context.

The application is responsible for enforcing governance rules around that answer.

A useful principle from the project is:

**Use the LLM for language generation; use deterministic controls for rules that must be consistently enforced.**

---

# 15. Source Attribution and Lineage

Initially, the LLM was allowed to generate source information itself.

Testing showed why this could be unreliable.

For example, the model could produce a policy citation or section reference that was not actually supported by the source document.

The design was changed so that the LLM is instructed to generate the answer without creating its own citation.

The application then adds the source using retrieved governance metadata.

Example:

Answer:

"Eligible employees may select from the health plans offered for the applicable plan year."

Application-generated source:

"Source: Health Insurance Policy, Version 1.7"

This creates a more controlled provenance path:

Answer  
↓  
Retrieved chunk  
↓  
Document name and version  
↓  
Source document  
↓  
Source repository  
↓  
Business owner

This connects RAG source attribution to traditional data-lineage concepts.


# 16. Why I Created an Evaluation Framework

A RAG application producing an answer does not automatically mean the system worked correctly.

I wanted to evaluate several separate questions:

- Did the system retrieve the expected authoritative document?
- Did it select the correct policy version?
- Was access control enforced?
- Did it reject unsupported questions?
- Was the generated answer grounded in the retrieved evidence?
- Was the answer clear and correct?
- How much of the retrieved context was actually relevant?

I created a six-case regression test set covering different governance scenarios.

---

# 17. The Six Test Scenarios

## T001 — Current PTO Policy

Question:

"How much vacation can I roll over to next year?"

Expected behavior:

- Retrieve PTO Policy
- Use current Version 3.0
- Answer 10 unused PTO days

Purpose:

Tests current-policy retrieval and version selection.

---

## T002 — Historical PTO Policy

Question:

"How many PTO days could employees carry over in 2025?"

Expected behavior:

- Retrieve PTO Policy
- Use historical Version 2.0
- Answer 5 unused PTO days

Purpose:

Tests temporal governance and use of a retired policy that was authoritative during the requested period.

---

## T003 — Remote Work Policy

Question:

"How many days a week can I work from home?"

Expected behavior:

- Retrieve Remote Work Policy Version 3.2
- Answer up to 3 regular workdays per week

Purpose:

Tests normal semantic retrieval against an approved policy.

---

## T004 — Unsupported Question

Question:

"What is the company's 2027 employee bonus percentage?"

Expected behavior:

- Do not manufacture an answer
- Return insufficient information
- Do not attach an unrelated source

Purpose:

Tests unsupported-question handling.

---

## T005 — Unauthorized Restricted Policy

Question:

"What does the Health Insurance Policy say about employee coverage?"

User group:

All Employees

Expected behavior:

- Do not expose the restricted Health Insurance Policy
- Return an insufficient-information response

Purpose:

Tests access control and source-substitution prevention.

---

## T006 — Authorized Restricted Policy

Same Health Insurance question, but the user belongs to the Benefits group.

Expected behavior:

- Retrieve Health Insurance Policy Version 1.7
- Generate an answer grounded in that policy
- Provide the governed source attribution

Purpose:

Confirms that the policy is accessible when the user is authorized.

---

# 18. Automated vs. Human Evaluation

Not every RAG quality measure should be evaluated the same way.

Some checks can be automated.

Automated checks in this project include:

- Expected document retrieval
- Expected version
- Access-control enforcement
- Unsupported-question rejection
- Access-denied response behavior
- Relevant chunk rate

Other measures require judgment about the generated response.

I manually reviewed supported-answer scenarios for:

### Groundedness

Does the retrieved evidence actually support the claims made in the generated answer?

### Answer Quality

Does the answer correctly and clearly respond to the user's question without introducing unsupported information?

This distinction is important because successful retrieval does not automatically guarantee a good generated answer.

---

# 19. Final Regression Results

After remediation, the six-case regression test produced:

| Metric | Result |
|---|---|
| Expected document retrieval | 4 / 4 applicable tests passed |
| Correct policy version | 4 / 4 applicable tests passed |
| Manual groundedness | 4 / 4 applicable tests passed |
| Manual answer quality | 4 / 4 applicable tests passed |
| Access-control enforcement | 1 / 1 applicable test passed |
| Access-denied response behavior | 1 / 1 applicable test passed |
| Unsupported-question rejection | 1 / 1 applicable test passed |
| Average relevant chunk rate | 55% |

The correct interpretation is:

**All applicable governance controls passed across the six-case regression test set after remediation.**

This should NOT be interpreted as:

**"The RAG system is 100% accurate."**

The evaluation set is intentionally small and uses fictional policy data.

---

# 20. Understanding the 55% Relevant Chunk Rate

For the four supported-answer tests, the relevant chunk rates were:

- T001 — 40%
- T002 — 100%
- T003 — 40%
- T006 — 40%

Average:

55%

This does NOT mean that only 55% of the answers were correct.

The expected authoritative document was retrieved in all four supported-answer scenarios.

Instead, the metric tells me about retrieval precision.

For example, suppose five chunks are retrieved and two come from the expected policy.

Relevant Chunk Rate:

2 / 5 = 40%

The correct evidence may still be present, allowing the system to produce the correct answer.

However, the remaining three chunks introduce retrieval noise.

Therefore:

**Document retrieval success = Did I retrieve the source I needed?**

**Relevant chunk rate = How much of what I retrieved was actually relevant?**

The project performed well on the first measure but showed room for improvement on the second.

This led to an important finding:

> The retriever consistently located the expected authoritative document, while chunk-level retrieval contained noise in several queries.

Possible future improvements include similarity thresholds, reranking, stronger metadata filtering, and retrieval tuning.

---

# 21. The Most Important Failure I Found

One of the most useful parts of the project was discovering behavior that looked acceptable initially but was not properly governed.

For the unauthorized Health Insurance question, access control successfully prevented the restricted Health Insurance Policy from being retrieved.

However, another benefits-related document could still be retrieved because it was semantically similar.

The LLM could then answer the Health Insurance question using the wrong policy.

This taught me:

**Preventing unauthorized retrieval is necessary, but it is not sufficient.**

The system must also verify that the evidence being used is appropriate for the question being asked.

I added requested-policy validation so that when a user explicitly asks about a known policy and that policy is unavailable after authorization and governance filtering, the application stops before calling the LLM.

---

# 22. Another Failure — Unsupported Questions and Citations

The unsupported bonus question also exposed an issue.

Because vector search returns the closest available chunks, the system could retrieve unrelated policy information even though no bonus policy existed.

The LLM could correctly say that there was insufficient information but still attach an unrelated source.

This creates misleading provenance.

The design was changed so that unsupported responses do not receive a source citation.

For this small prototype, a deterministic unsupported-topic control was also added for the bonus scenario.

The broader lesson is:

**A vector database returning a result does not mean the corpus contains an authoritative answer.**

---

# 23. Detect → Diagnose → Remediate → Regression Test

A useful way to describe the development process is:

**Detect**

Testing revealed incorrect or inconsistent behavior.

↓

**Diagnose**

I identified whether the issue came from retrieval, authorization, version selection, LLM generation, or citation logic.

↓

**Remediate**

I added or changed the appropriate governance control.

↓

**Regression Test**

I reran the evaluation set to confirm that the fix worked without breaking existing scenarios.

This is more important than simply saying:

"I built a RAG application."

It demonstrates that the application was treated as a governed data product whose behavior needed to be tested and monitored.

---

# 24. Tableau Governance & Quality Dashboard

The evaluation results were exported to CSV and visualized in Tableau.

The dashboard includes:

- Automated Governance Pass Rate
- Groundedness
- Average Relevant Chunk Rate
- Retrieval relevance by test scenario
- Governance test results
- Evaluation scope and interpretation notes

The dashboard separates governance-control success from retrieval quality.

For example:

Automated governance controls passed across the applicable regression tests.

At the same time:

Average relevant chunk rate was 55%.

Displaying both prevents a 100% governance-control pass rate from being misinterpreted as perfect overall RAG performance.

---

# 25. My Main Findings

The project produced several important lessons:

1. Semantic relevance and authoritative data are not the same thing.

2. Embeddings complement metadata; they do not replace governance metadata.

3. Retired information can still be authoritative for historical questions.

4. Access controls should be enforced before restricted information reaches the LLM.

5. Blocking restricted content is not enough if the system can substitute another source.

6. Correct document retrieval does not mean retrieval precision is perfect.

7. Correct retrieval does not guarantee grounded generation.

8. LLM-generated citations should not automatically be trusted.

9. Important governance rules are more reliable when enforced through application logic and metadata rather than prompting alone.

10. RAG systems need regression testing just like other enterprise data products.


# 26. Project File Map

Understanding the role of each file helps me trace the project from source data through retrieval and evaluation.

## data/policies/

Contains the fictional enterprise policy PDFs used as the RAG knowledge base.

Examples:

- PTO Policy
- Remote Work Policy
- Health Insurance Policy
- Employee Handbook
- Travel & Expense Policy

These represent the source data being governed.

---

## governance/document_catalog.csv

This is the governance catalog for the policy documents.

It stores metadata such as:

- Document ID
- Document name
- Business owner
- Classification
- Version
- Status
- Effective date
- Expiration date
- Review date
- Source system
- Access group

This file is important because the RAG application needs more than document text. It needs governance information to determine whether retrieved information is appropriate to use.

---

## governance/rag_governance_rules.md

Documents the governance rules the prototype is expected to enforce.

Examples include:

- Approved-document rules
- Historical-policy rules
- Access-control requirements
- Metadata and lineage requirements
- Unsupported-question behavior
- Source-attribution requirements
- Evaluation expectations

This is essentially the governance policy for the RAG prototype.

---

# 27. Python Files

## src/load_documents.py

Purpose:

Loads the source policy PDFs and extracts their text.

Conceptually:

PDF → Python → Extracted text

This represents the ingestion stage of the RAG pipeline.

---

## src/validate_catalog.py

Purpose:

Performs data-quality checks against the governance catalog.

Examples of checks include:

- Required metadata completeness
- Valid document statuses
- Presence of business owners
- Presence of classifications
- Date validation
- Version-related checks

This represents a governance/data-quality control before relying on the documents downstream.

---

## src/chunk_documents.py

Purpose:

Splits extracted policy text into smaller chunks.

The project uses approximately:

- 700-character chunks
- 100-character overlap

The script also preserves governance metadata with each chunk.

Conceptually:

Document

↓

Chunk 1 + metadata  
Chunk 2 + metadata  
Chunk 3 + metadata

Preserving metadata is critical for lineage and downstream governance filtering.

---

## src/build_vectorstore.py

Purpose:

Creates embeddings for the document chunks and stores them in ChromaDB.

Embedding model:

`all-MiniLM-L6-v2`

Vector database:

ChromaDB

Collection:

`acme_policy_chunks`

Conceptually:

Chunk + Metadata

↓

Embedding Model

↓

Vector + Chunk + Metadata

↓

ChromaDB

This prepares the governed enterprise content for semantic retrieval.

---

## src/rag_engine.py

This is the main RAG application logic.

It brings together:

- Question processing
- User access group
- Historical-year detection
- Query embedding
- Metadata/access filtering
- Semantic retrieval
- Temporal filtering
- Requested-policy validation
- Governed context construction
- Local LLM generation
- Unsupported-response controls
- Deterministic source attribution

This is the most important Python file in the finished prototype.

A simplified way to remember it is:

Question

↓

Governance filters

↓

Retrieve evidence

↓

Validate evidence

↓

LLM generates answer

↓

Application adds governed source

↓

Final response

---

## src/test_rag_engine.py

Purpose:

Provides a simple way to test the reusable RAG engine.

It was useful for validating individual scenarios before running the larger regression evaluation.

---

# 28. Evaluation Files

## evaluation/test_questions.csv

Contains the six regression-test scenarios.

Each row defines information such as:

- Test ID
- Question
- User group
- Expected document
- Expected version
- Expected answer
- Expected behavior
- Manual groundedness review
- Manual answer-quality review

This acts as the expected-results definition for the evaluation.

---

## evaluation/run_evaluation.py

Purpose:

Runs each test question through `rag_engine.py` and compares the output with expected behavior.

It evaluates measures such as:

- Document retrieval
- Version selection
- Relevant chunk rate
- Access-control behavior
- Unsupported-question rejection

It also combines automated results with the manually reviewed groundedness and answer-quality fields.

Conceptually:

Test Question

↓

rag_engine.py

↓

Actual Result

↓

Compare with Expected Result

↓

Evaluation Metrics

---

## evaluation/evaluation_results.csv

Contains the results generated by the evaluation script.

This file is also used as the data source for the Tableau governance dashboard.

Therefore the lineage continues:

RAG execution

↓

Evaluation results

↓

CSV

↓

Tableau

↓

Governance & Quality Dashboard

---

# 29. How the Main Files Connect

The overall relationship is:

`document_catalog.csv`

+

Policy PDFs

↓

`validate_catalog.py`

↓

`load_documents.py`

↓

`chunk_documents.py`

↓

`build_vectorstore.py`

↓

ChromaDB

↓

`rag_engine.py`

↓

Generated answer

At the same time:

`test_questions.csv`

↓

`run_evaluation.py`

↓

`rag_engine.py`

↓

`evaluation_results.csv`

↓

Tableau Dashboard

This gives me two related flows:

**RAG pipeline**

Source → Govern → Prepare → Retrieve → Generate

**Evaluation pipeline**

Define expected behavior → Execute → Compare → Measure → Monitor

---

# 30. Earlier Learning Files

Some additional Python files were created while learning and building the prototype.

Examples include:

- `test_embeddings.py`
- `test_chromadb.py`
- `retrieve.py`
- `rag.py`
- `read_catalog.py`

These represent earlier stages of the learning process rather than the final architecture.

They helped me understand the components separately before combining them into the governed RAG engine.

The learning progression was approximately:

Embedding experiment

↓

ChromaDB experiment

↓

Basic semantic retrieval

↓

Basic RAG

↓

Governed RAG

↓

Evaluation and monitoring

I am keeping these files for my own learning reference rather than treating them as the primary implementation.


