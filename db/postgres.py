import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config.settings import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB

def initialize_postgresql():
    try:
        conn = psycopg2.connect(
            dbname="postgres", user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{PG_DB}';")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {PG_DB};")
        conn.close()

        conn = psycopg2.connect(
            dbname=PG_DB, user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
        )
        cur = conn.cursor()
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                embedding VECTOR(1024),
                document TEXT
            );
            """
        )
        conn.commit()
        print("PostgreSQL initialized successfully.")
        return conn
    except Exception as e:
        print(f"Error initializing PostgreSQL: {e}")
