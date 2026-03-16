import streamlit as st
import os
from dotenv import load_dotenv
from snowflake.snowpark import Session

st.title("Support Ticket AI Agent")

# Load your secure passwords from the hidden .env file
load_dotenv()

# Define the bridge to Snowflake
connection_parameters = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "role": "ACCOUNTADMIN", 
    "warehouse": "COMPUTE_WH", 
    "database": "CRM_DB",
    "schema": "PUBLIC"
}

# Build the session with a safety check
session = None
try:
    session = Session.builder.configs(connection_parameters).create()
except Exception as e:
    st.error(f"Failed to connect to Snowflake. Check your .env file! Error: {e}")

# Only show the chat if the database connected successfully
if session:
    user_question = st.chat_input("Ask a question about support tickets")

    if user_question:
        st.chat_message("user").write(user_question)

        # SECURITY FIX: Escape single quotes so words like "What's" don't crash the SQL
        safe_question = user_question.replace("'", "''")

        sql_query = f"""
        WITH question_embedding AS (
            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', '{safe_question}') AS q_vec
        ),

        retrieved_tickets AS (
            SELECT
            Support_Ticket_Notes,
            VECTOR_COSINE_SIMILARITY(note_embedding, q_vec) AS similarity
            FROM CRM_DB.PUBLIC.SUPPORT_CASES, question_embedding
            ORDER BY similarity DESC
            LIMIT 5
        ),

        context AS (
            SELECT LISTAGG(Support_Ticket_Notes, '\\n\\n') AS tickets
            FROM retrieved_tickets
        )

        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'mistral-large',
            CONCAT(
                'You are a helpful Data Agent. Based ONLY on the following support tickets:\\n\\n',
                tickets,
                '\\n\\nAnswer the user question: {safe_question}'
            )
        ) AS answer
        FROM context
        """

        try:
            # Execute the query
            result = session.sql(sql_query).collect()
            answer = result[0]["ANSWER"]
            st.chat_message("assistant").write(answer)
        except Exception as e:
            st.error(f"Error running query: {e}")