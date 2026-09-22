from pathlib import Path

import pandas as pd
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# --------------------------------
# STEP 1: Load document catalog
# --------------------------------

catalog = pd.read_csv("governance/document_catalog.csv")

print("Documents in catalog:", len(catalog))


# --------------------------------
# STEP 2: Keep approved documents
# --------------------------------

approved_catalog = catalog[
    catalog["status"] == "Approved"
].copy()

print("Approved documents:", len(approved_catalog))


# --------------------------------
# STEP 3: Create text splitter
# --------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=100
)


# --------------------------------
# STEP 4: Create empty list
# --------------------------------

governed_chunks = []


# --------------------------------
# STEP 5: Process each approved PDF
# --------------------------------

for _, metadata_row in approved_catalog.iterrows():

    file_name = metadata_row["file_name"]

    pdf_path = Path("data/policies") / file_name

    print("\nProcessing:", file_name)

    # Make sure the PDF actually exists
    if not pdf_path.exists():

        print("WARNING: File not found:", file_name)

        continue


    # Read PDF
    reader = PdfReader(pdf_path)

    full_text = ""

    for page in reader.pages:

        text = page.extract_text()

        if text:
            full_text += text + "\n"


    # Split document
    chunks = text_splitter.split_text(full_text)

    print("Chunks created:", len(chunks))


    # Create governed chunk records
    for number, chunk in enumerate(chunks, start=1):

        document_id = metadata_row["document_id"]
        version = metadata_row["version"]

        chunk_id = (
            f"{document_id}_v{version}_chunk_{number:03}"
        )

        chunk_record = {

            "chunk_id":
                chunk_id,

            "text":
                chunk,

            "file_name":
                file_name,

            "document_id":
                document_id,

            "document_name":
                metadata_row["document_name"],

            "business_owner":
                metadata_row["business_owner"],

            "classification":
                metadata_row["classification"],

            "version":
                version,

            "status":
                metadata_row["status"],

            "effective_date":
                metadata_row["effective_date"],

            "source_system":
                metadata_row["source_system"],

            "access_group":
                metadata_row["access_group"]
        }

        governed_chunks.append(chunk_record)


# --------------------------------
# STEP 6: Summary
# --------------------------------

print("\n")
print("=" * 60)

print("TOTAL GOVERNED CHUNKS:", len(governed_chunks))

print("=" * 60)


# --------------------------------
# STEP 7: Show chunk summary
# --------------------------------

for record in governed_chunks:

    print(
        record["chunk_id"],
        "|",
        record["document_name"],
        "|",
        record["status"]
    )