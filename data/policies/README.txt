RAG GOVERNANCE TRAINING DATA — ACME FINANCIAL SERVICES

All documents are fictional and intended only for learning.

IMPORTANT TEST SCENARIOS
1. PTO_Policy_v3.pdf is the current approved version.
2. PTO_Policy_v2.pdf is retired and should not be used for current entitlement questions.
3. Version conflict test: v2 says 5 carryover days; v3 says 10.
4. The Employee Handbook provides high-level summaries; specific current policies should take precedence.
5. Health_Insurance_Policy is classified more restrictively than general Internal documents.
6. Remote Work Policy is current as of August 1, 2026.
7. Travel Expense and Business Travel policies are separate but related Finance documents.

Suggested metadata fields to extract:
document_id, owner, classification, version, status, effective_date, expiration_date, review_date, source_system, access_group.

Suggested RAG tests:
- What is the current PTO carryover limit?
- What was the PTO carryover limit under the 2025 policy?
- Can I work remotely 3 days a week?
- How many company holidays are observed in 2026?
- How long is paid parental leave?
- When should I submit an expense report?
- Can an employee access confidential health information?
- What happens when the handbook conflicts with a specific policy?
- Ask a question that is not covered and verify the system refuses to invent an answer.
