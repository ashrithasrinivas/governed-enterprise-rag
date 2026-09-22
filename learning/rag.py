import re
from datetime import datetime

import chromadb
import ollama
from sentence_transformers import SentenceTransformer


# --------------------------------
# STEP 1: Load embedding model
# --------------------------------

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# --------------------------------
# STEP 2: Connect to vector database
# --------------------------------

client = chromadb.PersistentClient(
    path="outputs/chroma_db"
)

collection = client.get_collection(
    name="acme_policy_chunks"
)


# --------------------------------
# STEP 3: Get user access group
# --------------------------------

user_group = input(
    "\nEnter your access group (All Employees or Benefits): "
).strip()

if user_group == "Benefits":
    allowed_groups = ["All Employees", "Benefits"]
else:
    allowed_groups = ["All Employees"]


# --------------------------------
# STEP 4: Ask user a question
# --------------------------------

question = input(
    "\nAsk a policy question: "
)
# --------------------------------
# Detect historical year
# --------------------------------

year_match = re.search(r"\b(20\d{2})\b", question)

if year_match:
    question_year = int(year_match.group(1))
    print("Historical year detected:", question_year)
else:
    question_year = None
    print("No historical year detected - using current policies")
# --------------------------------
# STEP 4: Create question embedding
# --------------------------------

question_embedding = embedding_model.encode(
    question
).tolist()


# --------------------------------
# STEP 5: Retrieve relevant chunks
# --------------------------------

if question_year is None:

    # Current question:
    # only use currently Approved policies
    retrieval_filter = {
        "$and": [
            {
                "access_group": {
                    "$in": allowed_groups
                }
            },
            {
                "status": "Approved"
            }
        ]
    }

else:

    # Historical question:
    # allow Approved and Retired policies.
    # The LLM will receive date metadata so that
    # the historically applicable version can be identified.
    retrieval_filter = {
        "$and": [
            {
                "access_group": {
                    "$in": allowed_groups
                }
            },
            {
                "status": {
                    "$in": ["Approved", "Retired"]
                }
            }
        ]
    }


results = collection.query(
    query_embeddings=[question_embedding],
    n_results=10,
    where=retrieval_filter
)

# --------------------------------
# Apply temporal governance
# --------------------------------

filtered_documents = []
filtered_metadatas = []

documents = results["documents"][0]
metadatas = results["metadatas"][0]

for document, metadata in zip(documents, metadatas):

    # Current question:
    # status filtering already limits results to Approved policies.
    if question_year is None:
        filtered_documents.append(document)
        filtered_metadatas.append(metadata)
        continue

    # Historical question:
    # determine whether the policy was valid at any point
    # during the requested year.

    effective_date = datetime.strptime(
        metadata["effective_date"],
        "%Y-%m-%d"
    ).date()

    expiration_value = metadata.get(
        "expiration_date",
        ""
    )

    if expiration_value:
        expiration_date = datetime.strptime(
            expiration_value,
            "%Y-%m-%d"
        ).date()
    else:
        expiration_date = None

    # Requested calendar year
    year_start = datetime(
        question_year, 1, 1
    ).date()

    year_end = datetime(
        question_year, 12, 31
    ).date()

    # Policy is eligible if its effective period
    # overlaps the requested calendar year.
    valid_for_year = (
        effective_date <= year_end
        and
        (
            expiration_date is None
            or expiration_date >= year_start
        )
    )

    if valid_for_year:
        filtered_documents.append(document)
        filtered_metadatas.append(metadata)


# Keep only the most relevant eligible chunks
filtered_documents = filtered_documents[:5]
filtered_metadatas = filtered_metadatas[:5]

# --------------------------------
# STEP 6: Build context for LLM
# --------------------------------

context_parts = []

for i in range(len(filtered_documents)):

    document = filtered_documents[i]
    metadata = filtered_metadatas[i]

    source_context = f"""
SOURCE {i + 1}
Policy: {metadata["document_name"]}
Version: {metadata["version"]}
Status: {metadata["status"]}
Effective Date: {metadata["effective_date"]}
Expiration Date: {metadata["expiration_date"]}
Owner: {metadata["business_owner"]}

Policy Text:
{document}
"""

    context_parts.append(source_context)


context = "\n".join(context_parts)

print("\n")
print("=" * 60)
print("RETRIEVED CONTEXT SENT TO LLM")
print("=" * 60)
print(context)
# --------------------------------
# STEP 7: Create governed prompt
# --------------------------------

prompt = f"""
You are an enterprise employee policy assistant.

Your task is to answer the user's question using ONLY the provided policy context.

IMPORTANT INSTRUCTIONS:

- Answer the specific question being asked.
- Use normal semantic equivalence when clearly supported by context.
  Examples:
  "vacation" may refer to PTO when the retrieved PTO policy
  directly addresses the user's question.
  "work from home" may refer to remote work.
- Do not require the user's wording to exactly match the policy wording.
- If a retrieved policy directly answers the question, give that answer.
- Do not claim information is missing when the retrieved context
  directly contains the answer.
- Do not add requirements, exceptions, or facts that are not present
  in the provided context.
- If the context truly does not contain the answer, respond with EXACTLY this sentence and nothing else:
  "The available policy documents do not contain enough information to answer this question."

- If you give the insufficient-information response above:
  DO NOT include a source or citation.

- ONLY when the context supports an answer, end the answer with:
  Source: <Policy Name>, Version <Version>

POLICY CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

# --------------------------------
# STEP 8: Send context to local LLM
# --------------------------------

response = ollama.chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)


# --------------------------------
# STEP 9: Display answer
# --------------------------------

print("\n")
print("=" * 60)
print("RAG ANSWER")
print("=" * 60)

answer = response["message"]["content"].strip()

insufficient_message = (
    "The available policy documents do not contain enough "
    "information to answer this question."
)

if answer.startswith(insufficient_message):
    answer = insufficient_message

print(answer)