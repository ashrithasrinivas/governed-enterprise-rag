# RAG Governance Rules

## Purpose

These rules define the governance controls applied to the fictional Acme Financial Services enterprise policy RAG prototype.

## 1. Authoritative Source Control

Policy answers must be based on documents registered in the governed document catalog.

Each document must include governance metadata such as:

- Document ID
- Document name
- Business owner
- Classification
- Version
- Status
- Effective date
- Expiration date, when applicable
- Source system
- Access group

## 2. Current Policy Rules

For questions about current policy requirements:

- Only Approved documents are eligible.
- Retired documents must not be used for current employee entitlements.
- The applicable current approved version is treated as authoritative.

## 3. Historical Policy Rules

For explicitly historical questions:

- Approved and Retired documents may be considered.
- The document must have been effective during the requested time period.
- A retired policy may be authoritative for a historical period even though it is no longer valid for current use.

## 4. Access Control

Access restrictions must be applied before restricted document content is supplied to the language model.

Users may retrieve only documents authorized for their access group.

Restricted content must not be exposed to an unauthorized user through the LLM context.

## 5. Metadata and Lineage

Governance metadata must remain associated with document chunks throughout ingestion and retrieval.

Retrieved content should be traceable through:

Answer → Retrieved Chunk → Document → Version → Source → Business Owner

## 6. Unsupported Questions

If the governed policy corpus does not contain sufficient information to answer a question, the system should return an insufficient-information response rather than generate an unsupported answer.

An unrelated retrieved document must not be presented as authoritative evidence for an unsupported question.

## 7. Source Attribution

For supported answers, source attribution should be generated from governed retrieval metadata rather than relying solely on the language model to generate policy names or versions.

For unsupported answers, no source citation should be presented.

## 8. Data Quality and Evaluation

The RAG workflow should be evaluated for:

- Expected document retrieval
- Correct policy version
- Retrieval relevance
- Access-control enforcement
- Unsupported-question rejection
- Groundedness
- Citation/source accuracy
- Answer quality

Evaluation results should distinguish automated controls from human-reviewed measures.

## 9. Change and Regression Testing

Changes to retrieval, filtering, prompting, or response controls should be regression tested against the defined evaluation set.

A remediation should not be considered complete until the affected scenario and existing governance scenarios are retested.