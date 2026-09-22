from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# User question
question = "How much vacation can I roll over to next year?"

# Possible policy chunks
pto_chunk = "Employees may carry over up to 10 unused PTO days."

remote_chunk = "Eligible employees may work remotely up to three days per week."

# Create embeddings
question_embedding = model.encode(question)
pto_embedding = model.encode(pto_chunk)
remote_embedding = model.encode(remote_chunk)

# Compare similarity
pto_similarity = cos_sim(
    question_embedding,
    pto_embedding
)

remote_similarity = cos_sim(
    question_embedding,
    remote_embedding
)

print("QUESTION:")
print(question)

print("\nPTO CHUNK:")
print(pto_chunk)
print("Similarity:", pto_similarity.item())

print("\nREMOTE WORK CHUNK:")
print(remote_chunk)
print("Similarity:", remote_similarity.item())