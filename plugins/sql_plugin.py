import os
import re
import pymysql
from dotenv import load_dotenv

# Semantic Kernel imports
import semantic_kernel as sk
import streamlit as st
from semantic_kernel.functions import kernel_function

load_dotenv()  # ensure AIVEN_* vars are available

# HOST = os.getenv("AIVEN_HOST")
# PORT = int(os.getenv("AIVEN_PORT", "3306"))
# USER = os.getenv("AIVEN_USER")
# PASSWORD = os.getenv("AIVEN_PASSWORD")
# DATABASE = os.getenv("AIVEN_DATABASE")

HOST=st.secrets["AIVEN_HOST"]
PORT = st.secrets["AIVEN_PORT"]
USER = st.secrets["AIVEN_USER"]
PASSWORD = st.secrets["AIVEN_PASSWORD"]
DATABASE = st.secrets["AIVEN_DATABASE"]


def get_connection():
    return pymysql.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        db=DATABASE,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
        read_timeout=10,
        write_timeout=10,
    )

class SqlPlugin:
    @kernel_function(name="get_schema", description="Return database schema as JSON")
    def get_schema(self) -> dict:
        schema = {}
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SHOW TABLES;")
                tables = [row[f"Tables_in_{DATABASE}"] for row in cur.fetchall()]
                for table in tables:
                    cur.execute(f"DESCRIBE `{table}`;")
                    cols = [
                        {"Field": r["Field"], "Type": r["Type"], "Null": r["Null"], "Key": r["Key"]}
                        for r in cur.fetchall()
                    ]
                    schema[table] = cols
        finally:
            conn.close()
        return schema

    @kernel_function(name="query_select", description="Execute a read-only SELECT query and return results")
    def query_select(self, sql_query: str) -> list:
        cleaned = sql_query.strip().lower()
        if not cleaned.startswith("select"):
            raise ValueError("Only SELECT queries are permitted.")
        if re.search(r"\b(delete|update|insert|drop|alter|create)\b", cleaned):
            raise ValueError("Only read-only SELECT queries are allowed.")
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql_query)
                return cur.fetchall()
        finally:
            conn.close()
