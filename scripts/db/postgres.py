from typing import Dict, List, Sequence
import psycopg2
from psycopg2 import sql
from config.settings import EMBEDDING_MODEL, EMBEDDING_PATH, PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB, PG_TABLE, PG_SCHEMA, STRUCTURED_DATA_PATH
from models.embeddings import generate_articles_with_embeddings

def initialize_postgresql(reset):
    try:
        # Connect to the target database
        with psycopg2.connect(
            dbname=PG_DB, user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
        ) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                if reset:
                        # Drop and recreate schema
                        cur.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE;").format(sql.Identifier(PG_SCHEMA)))
                        cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(sql.Identifier(PG_SCHEMA)))

                        # Enable the pgvector extension
                        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                        
                        value_names = {
                            'article_number': "article_number",
                            'title': "title",
                            'content': "content",
                            'refs': "refs",
                            'embedding': "embedding",
                        }
                        embedding_dim = 1024

                        # Create the table with dynamic embedding dimensions
                        cur.execute(sql.SQL(
                            f"""
                            CREATE TABLE IF NOT EXISTS {PG_SCHEMA}.{PG_TABLE} (
                                id SERIAL PRIMARY KEY,
                                {value_names['article_number']} TEXT NOT NULL,
                                {value_names['title']} TEXT NOT NULL,
                                {value_names['content']} TEXT NOT NULL,
                                {value_names['refs']} TEXT[],
                                {value_names['embedding']} VECTOR({embedding_dim})
                            );
                            """
                        ))
                        
                        # Process and insert embeddings
                        articles_with_embeddings = generate_articles_with_embeddings(
                            data_path=STRUCTURED_DATA_PATH, embedding_path=EMBEDDING_PATH, embedding_model=EMBEDDING_MODEL, value_names=value_names
                        )
                        insert_articles_with_embeddings(conn=conn, articles_with_embeddings=articles_with_embeddings, table_name=PG_TABLE, schema_name=PG_SCHEMA, value_names=value_names)#   
        print("Postgres initialized.")
        return conn
    except Exception as e:
        print(f"Failed to initialize PostgreSQL:")
        raise e

def insert_articles_with_embeddings(conn, articles_with_embeddings: List[Dict[str, Sequence[float]]], table_name: str, schema_name: str, value_names: List[str]):
    """
    Inserts articles and embeddings into PostgreSQL using pgvector.
    """
    if not conn:
        print("Invalid PostgreSQL connection. Skipping insertion.")
        return

    try:
        with conn.cursor() as pg_cur:
            for article in articles_with_embeddings:
                # Insert into PostgreSQL
                pg_cur.execute(sql.SQL("""
                    INSERT INTO {}.{} ({}, {}, {}, {}, {})
                    VALUES (%s, %s, %s, %s, %s::vector);
                """).format(
                    sql.Identifier(schema_name),
                    sql.Identifier(table_name),
                    sql.Identifier(value_names['article_number']),
                    sql.Identifier(value_names['title']),
                    sql.Identifier(value_names['content']),
                    sql.Identifier(value_names['refs']),
                    sql.Identifier(value_names['embedding']),
                ), (article.get(value_names['article_number']), article.get(value_names['title']), article.get(value_names['content']), article.get(value_names['refs']), article.get(value_names['embedding'])))
            conn.commit()
    except Exception as e:
        print(f"Error inserting articles into PostgreSQL: {e}")