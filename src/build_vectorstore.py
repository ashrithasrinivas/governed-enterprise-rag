from pathlib import Path

import pandas as pd
import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter


# --------------------------------
# STEP 1: Load metadata catalog
# --------------------------------

catalog = pd.read_csv("governance/document_catalog.csv")

# Include approved and retired documents.
# Retired documents may still be valid for historical questions.
eligible_catalog = catalog[
    catalog["status"].isin(["Approved", "Retired"])
].copy()

print("Documents available for RAG:", len(eligible_catalog))


# --------------------------------
# STEP 2: Load embedding model
# --------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------
# STEP 3: Create persistent ChromaDB
# --------------------------------

client = chromadb.PersistentClient(
    path="outputs/chroma_db"
)

collection = client.get_or_create_collection(
    name="acme_policy_chunks"
)


# --------------------------------
# STEP 4: Create text splitter
# --------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=100
)


# --------------------------------
# STEP 5: Process approved and retired PDFs
# --------------------------------
for _, metadata_row in eligible_catalog.iterrows():

    file_name = metadata_row["file_name"]
    pdf_path = Path("data/policies") / file_name

    print("\nProcessing:", file_name)

    if not pdf_path.exists():
        print("WARNING: File not found")
        continue

    # Extract text
    reader = PdfReader(pdf_path)

    full_text = ""

    for page in reader.pages:

        text = page.extract_text()

        if text:
            full_text += text + "\n"

    # Create chunks
    chunks = text_splitter.split_text(full_text)

    print("Chunks:", len(chunks))


    # --------------------------------
    # STEP 6: Embed and store chunks
    # --------------------------------

    for number, chunk in enumerate(chunks, start=1):

        document_id = str(metadata_row["document_id"])
        version = str(metadata_row["version"])

        chunk_id = (
            f"{document_id}_v{version}_chunk_{number:03}"
        )

        # Convert chunk text into embedding
        embedding = model.encode(chunk).tolist()

        # Governance metadata
        metadata = {
            "file_name": str(file_name),
            "document_id": document_id,
            "document_name": str(metadata_row["document_name"]),
            "business_owner": str(metadata_row["business_owner"]),
            "classification": str(metadata_row["classification"]),
            "version": version,
            "status": str(metadata_row["status"]),
            "effective_date": str(metadata_row["effective_date"]),
            "expiration_date": (
    ""
    if pd.isna(metadata_row["expiration_date"])
    else str(metadata_row["expiration_date"])
),
            "source_system": str(metadata_row["source_system"]),
            "access_group": str(metadata_row["access_group"])
        }

        # Store in ChromaDB
        collection.upsert(
            ids=[chunk_id],
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[metadata]
        )


# --------------------------------
# STEP 7: Show result
# --------------------------------

print("\n===================================")
print("VECTOR DATABASE CREATED")
print("===================================")

print("Total chunks stored:", collection.count())