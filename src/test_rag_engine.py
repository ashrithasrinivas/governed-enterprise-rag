from rag_engine import run_rag


result = run_rag(
    question="What does the health insurance policy say about employee coverage?",
    user_group="Benefits"
)


print("\n===================================")
print("RAG ENGINE TEST")
print("===================================")

print("\nAnswer:")
print(result["answer"])

print("\nRetrieved Sources:")

for metadata in result["metadatas"]:
    print(
        metadata["document_name"],
        "- Version",
        metadata["version"]
    )