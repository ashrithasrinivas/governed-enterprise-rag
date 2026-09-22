import pandas as pd

catalog = pd.read_csv("governance/document_catalog.csv")

print(catalog[["file_name", "business_owner", "version", "status"]])

approved_documents = catalog[catalog["status"] == "Approved"]

print("\nApproved Documents:")
print(approved_documents[["file_name", "version", "status"]])