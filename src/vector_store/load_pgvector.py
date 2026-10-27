import json
import os
import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# 1. Database Connection
conn = psycopg2.connect(
    host="127.0.0.1",
    port=5433,
    dbname="legal_rag_db",
    user="de_user",
    password="de_password"
)

cursor = conn.cursor()

# 2. Enable pgvector extension and create table
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS legal_sections (
        id SERIAL PRIMARY KEY,
        section_id VARCHAR(50),
        section_title TEXT,
        rag_text TEXT,
        embedding vector(384)
    );
""")
conn.commit()

# 3. Embedding model load karo (Free HuggingFace model)
print("Loading Embedding Model (all-MiniLM-L6-v2)...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

# 4. Gold JSON data read karo
with open("data/gold_ipc.json", "r", encoding="utf-8") as f:
    records = json.load(f)

print(f"Total {len(records)} records load ho rahe hain pgvector me...")

# 5. Insert records with vector embeddings
for item in records:
    text = item["rag_text"]
    vector = embed_model.encode(text).tolist()
    
    cursor.execute("""
        INSERT INTO legal_sections (section_id, section_title, rag_text, embedding)
        VALUES (%s, %s, %s, %s);
    """, (item["section_id"], item["section_title"], text, vector))

conn.commit()
cursor.close()
conn.close()

print("✅ Success! Saara Gold legal data pgvector me insert ho gaya!")