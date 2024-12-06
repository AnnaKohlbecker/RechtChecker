import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config.settings import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB
from models.embeddings import process_articles_with_embeddings


def initialize_postgresql(reset):
    """
    Initialize the PostgreSQL database and set up TimescaleDB.
    
    :param reset: If True, resets the database.
    """
    try:
        # Connect to the initial database specified in settings (default: postgres)
        conn = psycopg2.connect(
            dbname=PG_DB, user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        if reset:
            # Check and drop the target database if it exists
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = %s;", (PG_DB,))
            if cur.fetchone():
                print(f"Dropping existing database '{PG_DB}'...")

                # Terminate all active connections to the target database
                cur.execute(
                    """
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = %s
                      AND pid <> pg_backend_pid();
                    """,
                    (PG_DB,),
                )

                # Drop the database
                cur.execute(f"DROP DATABASE {PG_DB};")
                print(f"Database '{PG_DB}' dropped successfully.")

        # Create the target database
        print(f"Creating database '{PG_DB}'...")
        cur.execute(f"CREATE DATABASE {PG_DB};")
        conn.close()

        # Connect to the newly created database
        conn = psycopg2.connect(
            dbname=PG_DB, user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
        )
        cur = conn.cursor()

        # Enable TimescaleDB and other required extensions
        cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Create a hypertable
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                embedding VECTOR(1024),
                document TEXT,
                article_number TEXT,
                title TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
        cur.execute("SELECT create_hypertable('items', 'created_at', if_not_exists => TRUE);")
        conn.commit()
        print(f"Database '{PG_DB}' initialized with TimescaleDB successfully.")

        # Process and insert structured data
        structured_data_path = "data/GG_structured.json"
        embedding_model = "mxbai-embed-large:latest"
        articles_with_embeddings = process_articles_with_embeddings(structured_data_path, embedding_model)
        insert_documents_pg(conn, articles_with_embeddings)
        print("All articles inserted successfully.")

    except Exception as e:
        print(f"Error initializing PostgreSQL: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()


def insert_documents_pg(pg_conn, documents):
    """
    Inserts documents and embeddings into PostgreSQL.
    
    :param pg_conn: Connection to the PostgreSQL database.
    :param documents: List of dictionaries with 'embedding', 'document', 'article_number', and 'title'.
    """
    if not pg_conn:
        print("Invalid PostgreSQL connection. Skipping insertion.")
        return

    try:
        pg_cur = pg_conn.cursor()
        for doc in documents:
            embedding = doc.get("embedding")
            content = doc.get("content")
            article_number = doc.get("article_number")
            title = doc.get("title")

            # Insert into PostgreSQL
            pg_cur.execute(
                """
                INSERT INTO items (embedding, document, article_number, title) 
                VALUES (%s, %s, %s, %s);
                """,
                (embedding, content, article_number, title),
            )
        pg_conn.commit()
        print("Documents inserted successfully.")
        pg_conn.close()
    except Exception as e:
        print(f"Error inserting documents into PostgreSQL: {e}")
    finally:
        if 'pg_cur' in locals() and pg_cur:
            pg_cur.close()
