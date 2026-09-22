import re
from datetime import datetime

import chromadb
import ollama
from sentence_transformers import SentenceTransformer


# --------------------------------
# Load models and vector database
# --------------------------------

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(
    path="outputs/chroma_db"
)

collection = client.get_collection(
    name="acme_policy_chunks"
)


# --------------------------------
# Main reusable RAG function
# --------------------------------

def run_rag(question, user_group):

        # -----------------------------
    # Unsupported topic control
    # -----------------------------

    unsupported_topics = [
        "bonus"
    ]

    question_lower = question.lower()

    if any(
        topic in question_lower
        for topic in unsupported_topics
    ):
        insufficient_message = (
            "The available policy documents "
            "do not contain enough information "
            "to answer this question."
        )

        return {
            "question": question,
            "user_group": user_group,
            "answer": insufficient_message,
            "documents": [],
            "metadatas": []
        }

    # -----------------------------
    # Access control
    # -----------------------------

    if user_group == "Benefits":
        allowed_groups = [
            "All Employees",
            "Benefits"
        ]
    else:
        allowed_groups = [
            "All Employees"
        ]


    # -----------------------------
    # Detect historical year
    # -----------------------------

    year_match = re.search(
        r"\b(20\d{2})\b",
        question
    )

    if year_match:
        question_year = int(
            year_match.group(1)
        )
    else:
        question_year = None


    # -----------------------------
    # Create question embedding
    # -----------------------------

    question_embedding = (
        embedding_model
        .encode(question)
        .tolist()
    )


    # -----------------------------
    # Metadata retrieval filter
    # -----------------------------

    if question_year is None:

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

        retrieval_filter = {
            "$and": [
                {
                    "access_group": {
                        "$in": allowed_groups
                    }
                },
                {
                    "status": {
                        "$in": [
                            "Approved",
                            "Retired"
                        ]
                    }
                }
            ]
        }


    # -----------------------------
    # Retrieve candidate chunks
    # -----------------------------

    results = collection.query(
        query_embeddings=[
            question_embedding
        ],
        n_results=10,
        where=retrieval_filter
    )


    # -----------------------------
    # Temporal governance
    # -----------------------------

    filtered_documents = []
    filtered_metadatas = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    for document, metadata in zip(
        documents,
        metadatas
    ):

        if question_year is None:

            filtered_documents.append(
                document
            )

            filtered_metadatas.append(
                metadata
            )

            continue


        effective_date = datetime.strptime(
            metadata["effective_date"],
            "%Y-%m-%d"
        ).date()

        expiration_value = metadata.get(
            "expiration_date",
            ""
        )

        if expiration_value:

            expiration_date = (
                datetime.strptime(
                    expiration_value,
                    "%Y-%m-%d"
                ).date()
            )

        else:
            expiration_date = None


        year_start = datetime(
            question_year,
            1,
            1
        ).date()

        year_end = datetime(
            question_year,
            12,
            31
        ).date()


        valid_for_year = (
            effective_date <= year_end
            and
            (
                expiration_date is None
                or
                expiration_date >= year_start
            )
        )


        if valid_for_year:

            filtered_documents.append(
                document
            )

            filtered_metadatas.append(
                metadata
            )


    # Keep most relevant eligible chunks

    filtered_documents = (
        filtered_documents[:5]
    )

    filtered_metadatas = (
        filtered_metadatas[:5]
    )
    # -----------------------------
    # Requested-policy validation
    # -----------------------------

    known_policy_names = [
        "PTO Policy",
        "Parental Leave Policy",
        "Company Holiday Policy",
        "Remote Work Policy",
        "Benefits Eligibility Guide",
        "Health Insurance Policy",
        "Travel & Expense Policy",
        "Business Travel Policy",
        "Employee Handbook"
    ]

    requested_policy = None

    for policy_name in known_policy_names:
        if policy_name.lower() in question.lower():
            requested_policy = policy_name
            break


    if requested_policy:

        retrieved_policy_names = [
            metadata["document_name"]
            for metadata in filtered_metadatas
        ]

        if requested_policy not in retrieved_policy_names:

            insufficient_message = (
                "The available policy documents "
                "do not contain enough information "
                "to answer this question."
            )

            return {
                "question": question,
                "user_group": user_group,
                "answer": insufficient_message,
                "documents": filtered_documents,
                "metadatas": filtered_metadatas
            }

    # -----------------------------
    # Build LLM context
    # -----------------------------

    context_parts = []

    for i in range(
        len(filtered_documents)
    ):

        document = (
            filtered_documents[i]
        )

        metadata = (
            filtered_metadatas[i]
        )

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

        context_parts.append(
            source_context
        )


    context = "\n".join(
        context_parts
    )


    # -----------------------------
    # Governed prompt
    # -----------------------------

    prompt = f"""
You are an enterprise employee policy assistant.

Answer the user's question using ONLY the
provided policy context.

IMPORTANT INSTRUCTIONS:

- Answer the specific question being asked.

- Use normal semantic equivalence when clearly
  supported by context.

- "vacation" may refer to PTO when the retrieved
  PTO policy directly addresses the question.

- "work from home" may refer to remote work.

- Do not require the user's wording to exactly
  match the policy wording.

- If a retrieved policy directly answers the
  question, give that answer.

- Do not add requirements, exceptions, numbers,
  or facts not present in the context.

- If the context does not contain enough
  information, respond exactly:

"The available policy documents do not contain enough information to answer this question."

- Do not include a source, citation, policy name,
  version number, or section number in your answer.

- Answer only the user's question. Source attribution
  will be added separately by the application.

POLICY CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""


    # -----------------------------
    # Generate answer
    # -----------------------------

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = (
        response["message"]["content"]
        .strip()
    )


    # -----------------------------
    # Deterministic citation control
    # -----------------------------

    insufficient_message = (
        "The available policy documents "
        "do not contain enough information "
        "to answer this question."
    )

    insufficient_phrases = [
        "do not contain enough information",
        "does not contain enough information",
        "not enough information",
        "insufficient information",
        "no information available",
        "no information is available"
    ]

    answer_lower = answer.lower()

    if any(
        phrase in answer_lower
        for phrase in insufficient_phrases
    ):
        answer = insufficient_message


    else:
        source_metadata = filtered_metadatas[0]

        source_name = source_metadata[
            "document_name"
        ]

        source_version = source_metadata[
            "version"
        ]

        citation = (
            f"Source: {source_name}, "
            f"Version {source_version}"
        )

        answer = (
            f"{answer}\n\n{citation}"
        )

    


    # -----------------------------
    # Return evaluation information
    # -----------------------------

    return {
        "question": question,
        "user_group": user_group,
        "answer": answer,
        "documents": filtered_documents,
        "metadatas": filtered_metadatas
    }