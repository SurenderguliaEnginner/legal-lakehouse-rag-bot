import sys
import os

# Root directory ko path me add karo taaki src import ho sake
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from src.rag.rag_engine import ask_legal_rag

st.set_page_config(
    page_title="NyayaAI - Indian Legal Intelligence RAG",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS for polished look
st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; }
    .sub-title { font-size: 1rem; color: #64748B; margin-bottom: 25px; }
    .source-box { background-color: #F8FAFC; border-left: 4px solid #3B82F6; padding: 12px; border-radius: 4px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚖️ NyayaAI: Legal Lakehouse & Hybrid RAG</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Databricks Medallion Architecture ➔ PostgreSQL (pgvector) ➔ LLM Augmented Retrieval</div>', unsafe_allow_html=True)

# Sidebar with architectural details
with st.sidebar:
    st.header("🏗️ Platform Architecture")
    st.info("""
    - **Bronze/Silver/Gold:** Databricks Spark SQL (574 IPC Sections)
    - **Vector Store:** PostgreSQL 16 + pgvector (Port 5433)
    - **Embeddings:** all-MiniLM-L6-v2 (384-dimensions)
    - **Distance Metric:** Cosine Distance (`<=>`)
    - **Serving:** OpenRouter / OpenAI LLM
    """)
    st.success("🟢 Vector DB: Connected")

# User Input
user_query = st.text_input(
    "Ask a legal question in plain English:",
    placeholder="e.g., What is the punishment for theft or robbery?"
)

col1, col2 = st.columns([1, 5])
with col1:
    search_clicked = st.button("🔍 Get Legal Answer", type="primary")

if search_clicked and user_query:
    with st.spinner("Searching pgvector database and generating legal answer..."):
        try:
            answer, sources = ask_legal_rag(user_query)
            
            # Display LLM Answer
            st.subheader("📋 Legal Analysis & Provision:")
            st.write(answer)
            
            st.divider()
            
            # Display Retrieved Sources (Proof of RAG)
            st.subheader("📚 Verified IPC Sources Retrieved via pgvector:")
            for s in sources:
                with st.expander(f"IPC Section {s['section_id']}: {s['title']} (Cosine Distance: {s['distance']:.4f})"):
                    st.write(s['text'])
                    
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
            st.info("Make sure your OPENROUTER_API_KEY or OPENAI_API_KEY is saved in the .env file.")

