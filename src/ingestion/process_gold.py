import json
import os
import requests

# 1. Output directory ensure karo
os.makedirs("data", exist_ok=True)
GOLD_FILE = "data/gold_ipc.json"

print("1. Raw data fetch kar rahe hain...")
url = "https://raw.githubusercontent.com/civictech-India/Indian-Law-Penal-Code-Json/main/ipc.json"
raw_data = requests.get(url).json()

# 2. Wahi same logic jo Databricks me SQL se kiya tha
gold_records = []
for item in raw_data:
    desc = item.get("section_desc")
    # Khali rows ko chhod do (WHERE section_desc IS NOT NULL)
    if not desc or desc.strip() == "":
        continue
    
    sec_id = str(item.get("Section", "")).strip()
    sec_title = str(item.get("section_title", "")).strip()
    chapter = str(item.get("chapter_title", "")).strip()
    
    # CONCAT wala kaam: RAG ke liye clean paragraph context
    rag_text = f"Section: {sec_id} - {sec_title}. Chapter: {chapter}. Kanoon: {desc.strip()}"
    
    gold_records.append({
        "section_id": sec_id,
        "section_title": sec_title,
        "rag_text": rag_text
    })

# 3. Gold JSON file save kar do
with open(GOLD_FILE, "w", encoding="utf-8") as f:
    json.dump(gold_records, f, indent=2, ensure_ascii=False)

print(f"✅ Success! Gold data locally save ho gaya: {GOLD_FILE}")
print(f"Total Clean Records: {len(gold_records)}")