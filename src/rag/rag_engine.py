import os
import psycopg2
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

load_dotenv()

# 1. DB Connection Configuration
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5433,
    "dbname": "legal_rag_db",
    "user": "de_user",
    "password": "de_password",
}

# 2. Embedding Model (384 dimensions - same as ingestion)
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# 3. LLM Client Setup (OpenRouter or OpenAI auto-detect)
api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = "https://openrouter.ai/api/v1" if os.getenv("OPENROUTER_API_KEY") else None
model_name = "meta-llama/llama-3.1-8b-instruct:free" if os.getenv("OPENROUTER_API_KEY") else "gpt-4o-mini"

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

def retrieve_relevant_sections(query: str, top_k: int = 3):
    """User query ko embed karke pgvector se top_k legal sections fetch karta hai."""
    query_vector = embed_model.encode(query).tolist()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    sql = """
        SELECT section_id, section_title, rag_text, (embedding <=> %s::vector) AS distance
        FROM legal_sections
        ORDER BY distance ASC
        LIMIT %s;
    """
    cur.execute(sql, (str(query_vector), top_k))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "section_id": row[0],
            "section_title": row[1],
            "rag_text": row[2],
            "distance": round(float(row[3]), 4)
        })
    return results

def ask_legal_rag(query: str):
    """pgvector context fetch karta hai aur LLM se response generate karwata hai."""
    retrieved_docs = retrieve_relevant_sections(query, top_k=3)

    if not retrieved_docs:
        return "Database me koi relevant legal context nahi mila.", []

    # Context block banana
    context_str = "\n\n".join([
        f"[{doc['section_id']} - {doc['section_title']}]: {doc['rag_text']}"
        for doc in retrieved_docs
    ])

    system_prompt = (
        "You are an expert Indian Legal AI Assistant. Answer the user's question "
        "strictly based on the provided Indian Penal Code (IPC) context. "
        "Cite the relevant Section number clearly. If the context does not contain the answer, "
        "clearly state that IPC does not cover it in the retrieved documents."
    )

    user_prompt = f"LEGAL CONTEXT:\n{context_str}\n\nUSER QUESTION:\n{query}"

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    answer = response.choices[0].message.content
    return answer, retrieved_docs

if __name__ == "__main__":
    test_query = "What is the punishment for murder?"
    print(f"\n[?] Testing Query: '{test_query}'\n" + "-"*50)
    answer, docs = ask_legal_rag(test_query)
    print("\n[+] LLM ANSWER:\n", answer)
    print("\n[+] RETRIEVED SOURCES:")
    for d in docs:
        print(f" -> {d['section_id']}: {d['section_title']} (Distance: {d['distance']})")