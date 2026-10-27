# Databricks notebook source
import requests
import json

url = "https://raw.githubusercontent.com/civictech-India/Indian-Law-Penal-Code-Json/main/ipc.json"
response = requests.get(url)
data = response.json()

df_raw = spark.createDataFrame(data)

df_raw.write.format("delta").mode("overwrite").saveAsTable("bronze_ipc_raw")

print("Bronze Table Ban Gayi! Total records:", df_raw.count())
display(df_raw)

# COMMAND ----------


spark.sql("""
    CREATE OR REPLACE TABLE silver_ipc_cleaned AS
    SELECT 
        Section AS section_id,
        chapter AS chapter_no,
        chapter_title,
        section_title,
        section_desc
    FROM bronze_ipc_raw
    WHERE section_desc IS NOT NULL
""")

print("Silver Table Ban Gayi!")
display(spark.sql("SELECT * FROM silver_ipc_cleaned LIMIT 3"))

# COMMAND ----------

from pyspark.sql.functions import concat_ws, length

df_silver_clean = spark.table("silver_ipc_cleaned")

spark.sql("""
    CREATE OR REPLACE TABLE gold_ipc_rag AS
    SELECT 
        section_id,
        section_title,
        CONCAT(
            'Section: ', section_id, ' - ', section_title, 
            '. Chapter: ', chapter_title, 
            '. Kanoon: ', section_desc
        ) AS rag_text
    FROM silver_ipc_cleaned
""")

print("Gold Table Ban Gayi!")
display(spark.sql("SELECT section_id, rag_text FROM gold_ipc_rag"))

# COMMAND ----------


df_pandas = spark.sql("SELECT section_id, section_title, rag_text FROM gold_ipc_rag").toPandas()


import json
json_data = df_pandas.to_json(orient="records")


print("Sample JSON ready! Total records:", len(df_pandas))
print(df_pandas.head(2))

# COMMAND ----------


df_pandas.to_json("/tmp/gold_ipc.json", orient="records", indent=2)
with open("/tmp/gold_ipc.json", "r") as f:
    text = f.read()

print("File saved at /tmp/gold_ipc.json successfully!")

# COMMAND ----------

