# 🚀 Autonomous CRM RAG Pipeline: Salesforce to Snowflake Cortex

**Watch the 2-Minute Demo:** https://www.loom.com/share/c6526861eb3c4696bf1317e538f02bbd

## 📌 The Business Problem
Enterprise consulting teams spend countless hours manually extracting, reading, and analyzing unstructured CRM data (like support tickets and account notes) to assess client health. 

This project solves that by creating an **Autonomous RAG (Retrieval-Augmented Generation) Pipeline** that directly answers complex business questions using Salesforce data, eliminating manual data diving and accelerating decision-making.

## 🧠 Technical Architecture
This pipeline extracts mock Salesforce account and support data, vectorizes it for semantic search, and serves it through an AI-powered chat interface.


*(Note: Create a quick flowchart in Draw.io showing CSV -> Python -> Snowflake -> Cortex -> Streamlit, save it as architecture.png in your repo, and replace this line with: `![Architecture Diagram](architecture.png)`)*

## 🛠️ Tech Stack & Skills Demonstrated
* **Data Warehouse & AI:** Snowflake, Snowflake Cortex (`EMBED_TEXT_768`, `COMPLETE`)
* **Data Engineering:** Python (`pandas`, `snowflake-connector-python`), SQL, ETL automated scripting
* **Architecture:** RAG (Retrieval-Augmented Generation), Vector Similarity Search (`VECTOR_COSINE_SIMILARITY`)
* **Frontend:** Streamlit 

## ⚙️ How It Works (The Data Flow)
1. **Data Ingestion:** A Python script generates realistic, unstructured B2B CRM data (simulating Salesforce records) and securely loads it into a Snowflake database.
2. **Vectorization:** Snowflake Cortex processes the unstructured text notes and generates vector embeddings directly within the data warehouse.
3. **Semantic Retrieval:** When a user queries the Streamlit app, the input is vectorized and matched against the database using cosine similarity to retrieve the most relevant CRM context.
4. **LLM Generation:** The retrieved context is passed to a Snowflake Cortex LLM to generate a precise, hallucination-free answer with specific client details.

## 🚀 Quick Start (Local Setup)
To run this application locally, ensure you have a Snowflake account and Python 3.9+ installed.

```bash
# 1. Clone the repository
git clone [https://github.com/har1shhari/crm-cortex-rag-pipeline](https://github.com/YOUR_USERNAME/crm-cortex-rag-pipeline.git)

# 2. Navigate to the directory
cd crm-cortex-rag-pipeline

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your environment variables
# Create a .env file in the root directory and add your Snowflake credentials:
# SNOWFLAKE_USER="your_user"
# SNOWFLAKE_PASSWORD="your_password"
# SNOWFLAKE_ACCOUNT="your_account_identifier"

# 5. Run the Streamlit app
streamlit run app.py





👤 About the Author
Harishkumar Moorthy

MBA, International Business Management | B.E. Mechanical Engineering

Certified Salesforce Agentforce Specialist & Tableau CRM Consultant

Linkedin:(https://www.linkedin.com/in/harishkumar-moorthy-95255012b/)