# ⚖️ Enterprise Legal Lakehouse & Hybrid RAG Platform

An End-to-End Legal Q&A and Retrieval-Augmented Generation (RAG) system built over 574 sections of the Indian Penal Code (IPC). Designed from a **Data Engineer (1.5+ YOE)** perspective, focusing on scalable lakehouse batch processing, dense vector indexing, and zero-hallucination semantic search.

---

## 🏗️ Architecture Overview

```text
[ Raw IPC Legal Data (JSON) ]
              │
              ▼
   Databricks Medallion Lakehouse
   ├── Bronze : Raw Ingestion (Delta Lake)
   ├── Silver : Schema Standardization & Cleaning
   └── Gold   : Enriched & RAG-Ready Analytical Chunks
              │
              ▼
   Embedding Pipeline (all-MiniLM-L6-v2)
   384-dimensional dense semantic vectors
              │
              ▼
   PostgreSQL 16 + pgvector (Containerized via Docker)
   Indexed with Cosine Distance (`<=>`)
              │
              ▼
   Hybrid RAG Serving & LLM Generation (OpenAI / OpenRouter)
              │
              ▼
   Streamlit Interactive Legal Assistant UI
