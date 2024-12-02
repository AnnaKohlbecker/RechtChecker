import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config.settings import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB

def initialize_postgresql(reset=False):
    """
    Initialize the PostgreSQL database and ensure the necessary table and extension exist.

    :param reset: If True, drops the existing database before reinitializing.
    """
    try:
        # Connect to the default 'postgres' database
        conn = psycopg2.connect(
            dbname="postgres", user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        if reset:
            # Check if the database exists
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{PG_DB}';")
            if cur.fetchone():
                print(f"Dropping existing database '{PG_DB}'...")
                # Terminate active connections to the database
                cur.execute(
                    f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{PG_DB}'
                      AND pid <> pg_backend_pid();
                    """
                )
                # Drop the database
                cur.execute(f"DROP DATABASE {PG_DB};")
                print(f"Database '{PG_DB}' dropped successfully.")

        # Create the database
        print(f"Creating database '{PG_DB}'...")
        cur.execute(f"CREATE DATABASE {PG_DB};")
        conn.close()

        # Connect to the new database
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
        print(f"PostgreSQL database '{PG_DB}' initialized successfully.")
        return conn
    except Exception as e:
        print(f"Error initializing PostgreSQL: {e}")
        return None



def insert_documents_pg(pg_conn, documents):
    """
    Inserts documents with embeddings into PostgreSQL.

    :param pg_conn: Connection to the PostgreSQL database.
    :param documents: List of dictionaries containing 'embedding' and 'document'.
    """
    if not pg_conn:
        print("Invalid PostgreSQL connection. Skipping document insertion.")
        return

    try:
        pg_cur = pg_conn.cursor()
        for doc in documents:
            embedding = doc["embedding"]
            content = doc["content"]

            # Insert into PostgreSQL
            pg_cur.execute(
                "INSERT INTO items (embedding, document) VALUES (%s, %s);",
                (embedding, content)
            )
        pg_conn.commit()
        print("Documents inserted successfully into PostgreSQL.")
    except Exception as e:
        print(f"Error inserting documents into PostgreSQL: {e}")
    finally:
        if 'pg_cur' in locals() and pg_cur:
            pg_cur.close()

