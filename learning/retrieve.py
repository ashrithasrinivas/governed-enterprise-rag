import chromadb
from sentence_transformers import SentenceTransformer


# --------------------------------
# STEP 1: Load embedding model
# --------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------
# STEP 2: Connect to ChromaDB
# --------------------------------

client = chromadb.PersistentClient(
    path="outputs/chroma_db"
)

collection = client.get_collection(
    name="acme_policy_chunks"
)


# --------------------------------
# STEP 3: Ask a question
# --------------------------------

question = "How many days per week can I work from home?"

print("\nQUESTION:")
print(question)


# --------------------------------
# STEP 4: Convert question to embedding
# --------------------------------

question_embedding = model.encode(question).tolist()


# --------------------------------
# STEP 5: Search vector database
# --------------------------------

results = collection.query(
    query_embeddings=[question_embedding],
    n_results=3
)


# --------------------------------
# STEP 6: Display retrieved chunks
# --------------------------------

print("\nTOP RETRIEVED CHUNKS:")

for i in range(len(results["documents"][0])):

    document = results["documents"][0][i]
    metadata = results["metadatas"][0][i]
    distance = results["distances"][0][i]

    print("\n")
    print("=" * 60)

    print("RESULT:", i + 1)
    print("DOCUMENT:", metadata["document_name"])
    print("VERSION:", metadata["version"])
    print("STATUS:", metadata["status"])
    print("OWNER:", metadata["business_owner"])
    print("ACCESS:", metadata["access_group"])
    print("DISTANCE:", distance)

    print("\nTEXT:")
    print(document)