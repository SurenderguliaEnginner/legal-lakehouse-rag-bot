import os
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

# 1. Embedding Model load karo
print("Loading Embedding Model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 2. Database connection (.env se safe values)
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "5433")),
    dbname=os.getenv("DB_NAME", "legal_rag_db"),
    user=os.getenv("DB_USER", "de_user"),
    password=os.getenv("DB_PASS", "de_password")
)
cursor = conn.cursor()

# 3. Test Search Query
query = "What is the punishment for murder?"
query_vector = model.encode(query).tolist()

sql = """
    SELECT section_id, section_title, (embedding <=> %s::vector) AS distance
    FROM legal_sections
    ORDER BY distance ASC
    LIMIT 2;
"""

cursor.execute(sql, (str(query_vector),))
results = cursor.fetchall()

print("\n--- Search Results ---")
for r in results:
    print(f"Section {r[0]}: {r[1]} (Distance: {r[2]:.4f})")

cursor.close()
conn.close()