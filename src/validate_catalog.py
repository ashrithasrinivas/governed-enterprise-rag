import pandas as pd

# Load document catalog
catalog = pd.read_csv("governance/document_catalog.csv")

print("Total documents:", len(catalog))

# -----------------------------
# CHECK 1: Missing metadata
# -----------------------------

required_fields = [
    "file_name",
    "document_id",
    "document_name",
    "business_owner",
    "classification",
    "version",
    "status",
    "effective_date",
    "source_system",
    "access_group"
]

print("\n--- CHECK 1: REQUIRED METADATA ---")

for field in required_fields:

    missing_count = catalog[field].isna().sum()

    if missing_count == 0:
        print(field, ": PASS")
    else:
        print(field, ": FAIL -", missing_count, "missing value(s)")


# -----------------------------
# CHECK 2: Valid document status
# -----------------------------

print("\n--- CHECK 2: VALID STATUS ---")

valid_statuses = ["Approved", "Retired", "Draft"]

invalid_status = catalog[~catalog["status"].isin(valid_statuses)]

if len(invalid_status) == 0:
    print("Status validation: PASS")
else:
    print("Status validation: FAIL")
    print(invalid_status[["file_name", "status"]])


# -----------------------------
# CHECK 3: Business owner
# -----------------------------

print("\n--- CHECK 3: BUSINESS OWNER ---")

missing_owner = catalog[catalog["business_owner"].isna()]

if len(missing_owner) == 0:
    print("Business owner validation: PASS")
else:
    print("Business owner validation: FAIL")
    print(missing_owner["file_name"])


# -----------------------------
# CHECK 4: Classification
# -----------------------------

print("\n--- CHECK 4: CLASSIFICATION ---")

missing_classification = catalog[catalog["classification"].isna()]

if len(missing_classification) == 0:
    print("Classification validation: PASS")
else:
    print("Classification validation: FAIL")
    print(missing_classification["file_name"])

# -----------------------------
# CHECK 5: EFFECTIVE DATE
# -----------------------------

print("\n--- CHECK 5: EFFECTIVE DATE ---")

today = pd.Timestamp.today().normalize()

catalog["effective_date"] = pd.to_datetime(
    catalog["effective_date"],
    errors="coerce"
)

future_documents = catalog[
    catalog["effective_date"] > today
]

if len(future_documents) == 0:
    print("Effective date validation: PASS")
else:
    print("Documents not yet effective:")

    print(
        future_documents[
            ["file_name", "effective_date"]
        ]
    )

    # -----------------------------
# CHECK 6: EXPIRATION DATE
# -----------------------------

print("\n--- CHECK 6: EXPIRATION DATE ---")

catalog["expiration_date"] = pd.to_datetime(
    catalog["expiration_date"],
    errors="coerce"
)

expired_documents = catalog[
    catalog["expiration_date"].notna()
    & (catalog["expiration_date"] < today)
]

if len(expired_documents) == 0:
    print("Expiration validation: PASS")
else:
    print("Expired documents found:")

    print(
        expired_documents[
            ["file_name", "expiration_date", "status"]
        ]
    )

    # -----------------------------
# CHECK 7: REVIEW / FRESHNESS
# -----------------------------

print("\n--- CHECK 7: DOCUMENT FRESHNESS ---")

catalog["review_date"] = pd.to_datetime(
    catalog["review_date"],
    errors="coerce"
)

approved_documents = catalog[
    catalog["status"] == "Approved"
]

overdue_reviews = approved_documents[
    approved_documents["review_date"].notna()
    & (approved_documents["review_date"] < today)
]

if len(overdue_reviews) == 0:
    print("Freshness validation: PASS")
else:
    print("Documents requiring review:")

    print(
        overdue_reviews[
            ["file_name", "review_date", "business_owner"]
        ]
    )
    # -----------------------------
# CHECK 8: MULTIPLE VERSIONS
# -----------------------------

print("\n--- CHECK 8: MULTIPLE VERSIONS ---")

version_counts = (
    catalog.groupby("document_id")
    .size()
    .reset_index(name="version_count")
)

multiple_versions = version_counts[
    version_counts["version_count"] > 1
]

if len(multiple_versions) == 0:
    print("No multiple versions found.")
else:
    print("Documents with multiple versions:")

    print(multiple_versions)

    # -----------------------------
# CHECK 9: MULTIPLE APPROVED VERSIONS
# -----------------------------

print("\n--- CHECK 9: MULTIPLE APPROVED VERSIONS ---")

approved = catalog[
    catalog["status"] == "Approved"
]

approved_counts = (
    approved.groupby("document_id")
    .size()
    .reset_index(name="approved_count")
)

conflicts = approved_counts[
    approved_counts["approved_count"] > 1
]

if len(conflicts) == 0:
    print("Approved version validation: PASS")
else:
    print("WARNING: Multiple approved versions found!")

    print(conflicts)

print("\nCatalog validation complete.")