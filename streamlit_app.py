import streamlit as st
from snowflake.snowpark.context import get_active_session

st.title("Support Ticket AI Agent")

session = get_active_session()

user_question = st.chat_input("Ask a question about support tickets")

if user_question:

    st.chat_message("user").write(user_question)

    sql_query = f"""
    WITH question_embedding AS (
        SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', '{user_question}') AS q_vec
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
            '\\n\\nAnswer the user question: {user_question}'
        )
    ) AS answer
    FROM context
    """

    result = session.sql(sql_query).collect()

    answer = result[0]["ANSWER"]

    st.chat_message("assistant").write(answer)