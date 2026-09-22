from pathlib import Path
from pypdf import PdfReader

# Folder containing our policy documents
pdf_folder = Path("data/policies")

# Find every PDF in the folder
pdf_files = list(pdf_folder.glob("*.pdf"))

print("Number of PDF files found:", len(pdf_files))
print("-" * 50)

# Read each PDF
for pdf_file in pdf_files:

    print("Reading:", pdf_file.name)

    reader = PdfReader(pdf_file)

    full_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            full_text += text + "\n"

    print("Characters extracted:", len(full_text))
    print("-" * 50)