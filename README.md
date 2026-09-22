# Governed Enterprise Policy RAG Assistant

## Project Overview

This hands-on prototype explores how enterprise data governance principles can be applied to a Retrieval-Augmented Generation (RAG) application.

Using fictional Acme Financial Services policy documents, I built a local RAG workflow that combines semantic retrieval with governance controls for metadata, document ownership, policy versioning, effective dates, access control, source attribution, and evaluation.

The project focuses on a key enterprise AI question:

**How do we ensure an LLM receives information that is authoritative, current, permitted, traceable, and appropriate for the user's question?**

Key capabilities demonstrated:

- Governed document ingestion and metadata preservation
- Current vs. historical policy retrieval
- Policy version and effective-date controls
- Access filtering before LLM generation
- Unsupported-question handling
- Deterministic source attribution
- Retrieval, groundedness, and answer-quality evaluation

## Governance & Quality Dashboard

The prototype includes a Tableau dashboard for monitoring governance controls, groundedness, and retrieval quality across the regression test set.

![RAG Governance & Quality Dashboard](assets/rag-governance-dashboard.png)

The dashboard intentionally separates governance-control success from retrieval quality. In the six-case prototype, all applicable automated governance checks passed after remediation, while the average relevant chunk rate was 55%, highlighting an opportunity to improve retrieval precision.

## What I Built

I implemented the prototype end to end using Python and local AI tooling:

- Created a fictional enterprise policy corpus with current, historical, and restricted documents
- Built a governance catalog containing ownership, classification, version, status, effective-date, and access metadata
- Extracted and chunked policy documents while preserving governance metadata
- Generated embeddings and stored governed chunks in ChromaDB
- Implemented access, status, version, and temporal filtering before LLM generation
- Added deterministic controls for unsupported questions and source attribution
- Built a reusable RAG workflow using Ollama for local LLM inference
- Created a six-case regression test suite covering retrieval and governance behavior
- Analyzed evaluation results and built a Tableau governance and quality dashboard

## Business Problem

Enterprise RAG applications may retrieve information from multiple documents, versions, and data sources. Without appropriate governance controls, a system could:

- Retrieve an outdated policy instead of the current approved version
- Expose restricted information to unauthorized users
- Generate an answer from irrelevant documents
- Provide an answer without reliable source attribution
- Generate unsupported information when the source data does not contain an answer

This prototype explores how traditional data governance concepts such as metadata management, ownership, classification, lineage, data quality, access control, and lifecycle management can be extended to a RAG workflow.

## RAG Architecture

The prototype follows this workflow:

Policy PDFs  
↓  
Text Extraction  
↓  
Governance Metadata  
↓  
Chunking  
↓  
Embeddings  
↓  
Chroma Vector Database  
↓  
Access and Metadata Filtering  
↓  
Temporal / Version Filtering  
↓  
Semantic Retrieval  
↓  
Governed Context  
↓  
Local LLM Generation  
↓  
Deterministic Source Attribution  
↓  
Evaluation and Monitoring

The application uses governance metadata throughout the retrieval process rather than relying only on semantic similarity.

## Governance Controls

### 1. Metadata and Ownership

Each policy is registered in a document catalog with metadata including document ID, document name, business owner, classification, version, status, effective date, expiration date, source system, and access group.

Metadata is preserved when documents are chunked so retrieved content can be traced back to its governing source.

### 2. Version and Temporal Governance

Current questions retrieve approved policies. Historical questions can retrieve retired policies when the policy was valid during the requested period.

For example:

- A current PTO question uses PTO Policy Version 3.0.
- A question about PTO rules in 2025 uses retired PTO Policy Version 2.0.

This prevents the latest policy from automatically being applied to historical questions.

### 3. Access Control

Retrieval is filtered based on the user's access group before restricted content is provided to the language model.

For example, the Health Insurance Policy is classified as confidential employee-benefits information and is available only to the Benefits access group in this prototype.

### 4. Unsupported Questions

Questions that cannot be supported by the governed policy corpus return an insufficient-information response rather than presenting unrelated retrieved documents as authoritative evidence.

### 5. Source Attribution

The language model generates the natural-language answer, while source attribution is added programmatically using retrieved governance metadata.

Example:

`Source: Health Insurance Policy, Version 1.7`

This reduces reliance on the language model for provenance information such as policy names and versions.

## Evaluation Framework

A six-case regression test set was created to evaluate both RAG behavior and governance controls.

The test scenarios include:

- Current-policy retrieval
- Historical-policy and version retrieval
- Remote-work policy retrieval
- Unsupported-question rejection
- Unauthorized access to a restricted policy
- Authorized access to a restricted policy

Evaluation combines automated governance checks with human review.

### Automated Checks

The automated evaluation tests:

- Expected document retrieval
- Expected policy version
- Access-control enforcement
- Unsupported-question rejection
- Access-denied response behavior
- Relevant chunk rate

### Human-Reviewed Checks

Generated answers for supported-answer scenarios are manually reviewed for:

- Groundedness — whether claims in the answer are supported by retrieved context
- Answer quality — whether the response correctly and clearly answers the question without introducing unsupported information


## Evaluation Results

The final six-case regression test produced the following results:

| Metric | Result |
|---|---|
| Expected document retrieval | 4 / 4 applicable tests passed |
| Correct policy version | 4 / 4 applicable tests passed |
| Manual groundedness review | 4 / 4 applicable tests passed |
| Manual answer-quality review | 4 / 4 applicable tests passed |
| Access-control enforcement | 1 / 1 applicable test passed |
| Access-denied response behavior | 1 / 1 applicable test passed |
| Unsupported-question rejection | 1 / 1 applicable test passed |
| Average relevant chunk rate | 55% |

The results should be interpreted within the scope of this small six-case prototype and should not be interpreted as 100% overall RAG accuracy.

### Retrieval Quality Finding

The expected authoritative document was retrieved in all four supported-answer scenarios. However, the average relevant chunk rate was 55%.

Individual relevant chunk rates were:

- T001 — 40%
- T002 — 100%
- T003 — 40%
- T006 — 40%

This indicates that the retriever consistently located the expected authoritative source, but several queries also retrieved irrelevant chunks. Improving retrieval precision is therefore an identified opportunity for future work.

## Example Governance Scenario

A historical PTO question demonstrates the interaction between semantic retrieval and governance metadata.

Question:

`How many PTO days could employees carry over in 2025?`

The vector database contains both the retired PTO Policy Version 2.0 and the current Version 3.0.

Temporal governance determines that Version 2.0 was effective during 2025. The system therefore answers using the historical policy:

`Employees could carry over up to 5 unused PTO days.`

For a current PTO question, Version 3.0 is used instead, which allows up to 10 unused PTO days.

This demonstrates why semantic similarity alone is insufficient for governed enterprise retrieval.


## Technology Stack

- Python
- PyPDF
- Pandas
- Sentence Transformers
- all-MiniLM-L6-v2 embeddings
- ChromaDB
- Ollama
- Llama 3.2 3B
- LangChain Text Splitters
- Tableau
- VS Code

The RAG workflow runs locally for this prototype. Ollama is used for local language-model inference, while ChromaDB provides persistent vector storage.

## Project Structure

rag-governance-project/

- `data/policies/` — fictional enterprise policy documents
- `governance/` — document catalog and governance rules
- `src/` — ingestion, chunking, vector-store, RAG, and validation logic
- `evaluation/` — regression test set, evaluation script, and evaluation results
- `learning/` — incremental scripts used while learning and developing the RAG workflow
- `assets/` — portfolio images and dashboard screenshot
- `outputs/` — locally generated Chroma vector database (not committed)
- `PROJECT_NOTES.md` — detailed project study and interview-review notes
- `README.md` — portfolio documentation


## What Testing Revealed

Regression testing exposed governance issues that were not obvious from testing retrieval alone.

One scenario showed that blocking access to a restricted Health Insurance Policy was not sufficient. Semantic retrieval could still return a different benefits-related document and allow the system to answer from the wrong source. I added requested-policy validation so that when a user explicitly asks about a known policy, the expected authorized policy must be present in the governed retrieval results before generation proceeds.

Testing also showed that allowing the LLM to generate its own source information could produce unreliable provenance details. Source attribution was therefore moved out of the LLM prompt and generated programmatically from retrieved governance metadata.

These findings reinforced a core design principle used in the prototype:

**Use the LLM for language generation; use deterministic application logic and governed metadata for controls that require consistent enforcement.**

The development cycle followed:

**Detect → Diagnose → Remediate → Regression Test**

## Limitations and Future Improvements

This is a learning prototype built with a small fictional policy corpus and a six-case regression test set. It is not intended to represent a production enterprise RAG platform.

Current limitations include:

- Small document corpus and evaluation set
- Retrieval contains irrelevant chunks for several queries
- Unsupported-topic handling is simplified for the prototype
- Citation generation currently uses retrieved metadata and assumes a primary supporting source
- Access control uses simplified access groups rather than integration with an enterprise identity platform
- Groundedness and answer quality are manually reviewed
- Local LLM behavior may vary between runs

Potential future improvements include:

- Expanding the regression test set
- Introducing retrieval similarity thresholds
- Evaluating reranking to improve chunk precision
- Strengthening claim-to-source citation mapping
- Integrating enterprise identity and authorization controls
- Adding automated evaluation alongside human review
- Monitoring policy freshness and review dates
- Building alerts for governance-control failures


## Key Learning

The project demonstrates that governing a RAG application requires more than selecting an LLM or creating embeddings.

Reliable enterprise RAG depends on governing the information supplied to the model: identifying authoritative sources, preserving metadata and lineage, enforcing access controls, selecting valid document versions, measuring retrieval quality, and validating whether generated answers are supported by retrieved evidence.

The prototype applies familiar enterprise data-governance principles across the RAG lifecycle and demonstrates how Data Owner and data-governance responsibilities can extend into AI-enabled applications.
