import sys
from pathlib import Path

import pandas as pd


# --------------------------------
# Allow evaluation script to use src
# --------------------------------

project_root = Path(__file__).resolve().parents[1]

sys.path.append(
    str(project_root / "src")
)

from rag_engine import run_rag


# --------------------------------
# Load evaluation test set
# --------------------------------

tests = pd.read_csv(
    project_root
    / "evaluation"
    / "test_questions.csv"
)


# --------------------------------
# Run each test
# --------------------------------

print("\n===================================")
print("RAG EVALUATION")
print("===================================\n")

evaluation_results = []
for _, test in tests.iterrows():

    print("\n-----------------------------------")
    print("Test ID:", test["test_id"])
    print("-----------------------------------")

    print("Question:")
    print(test["question"])

    print("\nUser Group:")
    print(test["user_group"])


    result = run_rag(
        question=test["question"],
        user_group=test["user_group"]
    )


    print("\nGenerated Answer:")
    print(result["answer"])


    print("\nRetrieved Sources:")
    retrieved_documents = [
        metadata["document_name"]
        for metadata in result["metadatas"]
    ]

    retrieved_versions = [
        metadata["version"]
        for metadata in result["metadatas"]
    ]

    retrieved_context = "\n\n--- CHUNK ---\n\n".join(
        result["documents"]
    )
    # --------------------------------
    # Basic automated evaluation
    # --------------------------------

    expected_document = str(
        test["expected_document"]
    )

    expected_version = str(
        test["expected_version"]
    )

    manual_groundedness = test["manual_groundedness"]
    manual_answer_quality = test["manual_answer_quality"]

    # Document retrieval check
    if expected_document == "NONE":
        document_pass = "N/A"
    elif expected_document in retrieved_documents:
        document_pass = "PASS"
    else:
        document_pass = "FAIL"

    # --------------------------------
    # Relevant chunk rate
    # --------------------------------

    if expected_document == "NONE":
        relevant_chunk_rate = None

    else:
        relevant_chunks = sum(
            document == expected_document
            for document in retrieved_documents
        )

        if len(retrieved_documents) > 0:
            relevant_chunk_rate = round(
                (
                    relevant_chunks
                    / len(retrieved_documents)
                ) * 100,
                1
            )
        else:
            relevant_chunk_rate = 0.0

    # Version check
    if expected_version == "NONE":
        version_pass = "N/A"
    elif expected_version in retrieved_versions:
        version_pass = "PASS"
    else:
        version_pass = "FAIL"

    # --------------------------------
    # Access control check
    # --------------------------------

    if test["expected_behavior"] == "Access Denied":

        restricted_document = "Health Insurance Policy"

        if restricted_document in retrieved_documents:
            access_control_pass = "FAIL"
        else:
            access_control_pass = "PASS"

    else:
        access_control_pass = "N/A"

        # --------------------------------
    # Rejection behavior check
    # --------------------------------

    if test["expected_behavior"] == "Reject":

        answer_lower = result["answer"].lower()

        rejection_phrases = [
            "do not contain enough information",
            "does not contain enough information",
            "not specified",
            "insufficient information"
        ]

        if any(
            phrase in answer_lower
            for phrase in rejection_phrases
        ):
            rejection_pass = "PASS"
        else:
            rejection_pass = "FAIL"

    else:
        rejection_pass = "N/A"

        # --------------------------------
    # Access-denied response behavior
    # --------------------------------

    if test["expected_behavior"] == "Access Denied":

        answer_lower = result["answer"].lower()

        insufficient_phrases = [
            "do not contain enough information",
            "does not contain enough information",
            "not enough information",
            "insufficient information"
        ]

        if any(
            phrase in answer_lower
            for phrase in insufficient_phrases
        ):
            response_behavior_pass = "PASS"
        else:
            response_behavior_pass = "FAIL"

    else:
        response_behavior_pass = "N/A"

    evaluation_results.append({
        "test_id": test["test_id"],
        "question": test["question"],
        "user_group": test["user_group"],
        "expected_document": test["expected_document"],
        "expected_version": test["expected_version"],
        "expected_behavior": test["expected_behavior"],
        "expected_answer": test["expected_answer"],
        "generated_answer": result["answer"],
        "retrieved_documents": " | ".join(retrieved_documents),
        "retrieved_context": retrieved_context,
        "retrieved_versions": " | ".join(retrieved_versions),
        "document_pass": document_pass,
        "relevant_chunk_rate": relevant_chunk_rate,
        "manual_groundedness": manual_groundedness,
        "manual_answer_quality": manual_answer_quality,
        "version_pass": version_pass,
        "access_control_pass": access_control_pass,
        "rejection_pass": rejection_pass,
        "response_behavior_pass": response_behavior_pass
    })

        # --------------------------------
    # Access control check
    # --------------------------------

    if test["expected_behavior"] == "Access Denied":

        restricted_document = (
            "Health Insurance Policy"
        )

        if restricted_document in retrieved_documents:
            access_control_pass = "FAIL"
        else:
            access_control_pass = "PASS"

    else:
        access_control_pass = "N/A"

    for metadata in result["metadatas"]:

        print(
            "-",
            metadata["document_name"],
            "| Version",
            metadata["version"],
            "| Status",
            metadata["status"]
        )


print("\n===================================")
results_df = pd.DataFrame(
    evaluation_results
)

output_file = (
    project_root
    / "evaluation"
    / "evaluation_results.csv"
)

results_df.to_csv(
    output_file,
    index=False
)

print(
    "\nResults saved to:",
    output_file
)
print("Evaluation complete")
print("===================================")