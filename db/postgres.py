# from typing import Dict, List, Sequence
# import psycopg2
# from psycopg2 import sql
# from config.settings import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB, PG_TABLE, PG_SCHEMA
# from models.embeddings import process_articles_with_embeddings

# def initialize_postgresql(reset, data_path):
#     try:
#         # Connect to the target database directly
#         with psycopg2.connect(
#             dbname=PG_DB, user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
#         ) as conn:
#             conn.autocommit = True
#             with conn.cursor() as cur:
#                 if reset:              
#                     # Get all table names from the specified schema
#                     cur.execute(sql.SQL("""
#                         SELECT tablename 
#                         FROM pg_tables 
#                         WHERE schemaname = %s;
#                     """), [PG_SCHEMA])
#                     tables = cur.fetchall()
                    
#                     # Truncate all tables
#                     for table in tables:
#                         cur.execute(sql.SQL("TRUNCATE TABLE {}.{} CASCADE;").format(
#                             sql.Identifier(PG_SCHEMA),
#                             sql.Identifier(table[0])
#                         ))
                        
#                     #Create the schema if it does not exist
#                     cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(
#                         sql.Identifier(PG_SCHEMA)
#                     ))
                    
#                     #Create the table if it does not exist
#                     cur.execute(sql.SQL(
#                         f"""
#                         CREATE TABLE IF NOT EXISTS {PG_SCHEMA}.{PG_TABLE} (
#                             id SERIAL PRIMARY KEY,
#                             embedding FLOAT8[] NOT NULL,
#                             document TEXT NOT NULL,
#                             article_number INT,
#                             title TEXT
#                         );
#                         """
#                     ))
                    
#                     # Re-enable constraints
#                     cur.execute("SET session_replication_role = 'origin';")
#                     print(f"All data cleared from the database '{PG_DB}'.")
#                     articles_with_embeddings = process_articles_with_embeddings(data_path=data_path, embedding_model="mxbai-embed-large:latest")
#                     insert_articles_with_embeddings(conn, articles_with_embeddings, PG_TABLE, PG_SCHEMA)
            
#         print("Postgres initialized.")
                    
#     except psycopg2.Error as e:
#         print(f"Database error: {e}")

# def insert_articles_with_embeddings(pg_conn, articles_with_embeddings: List[Dict[str, Sequence[float]]], table_name: str, schema_name: str):
#     """
#     Inserts articles and embeddings into PostgreSQL.
#     """
#     if not pg_conn:
#         print("Invalid PostgreSQL connection. Skipping insertion.")
#         return

#     try:
#         print(f"Inserting embeddings into PostgreSQL table '{schema_name}.{table_name}'...")
#         pg_cur = pg_conn.cursor()
#         for article in articles_with_embeddings:
#             embedding = article.get("embedding")
#             content = article.get("content")
#             article_number = article.get("article_number")
#             title = article.get("title")

#             # Insert into PostgreSQL
#             pg_cur.execute(sql.SQL("""
#                 INSERT INTO {}.{} (embedding, document, article_number, title) 
#                 VALUES (%s, %s, %s, %s);
#             """).format(
#                 sql.Identifier(schema_name),
#                 sql.Identifier(table_name)
#             ), (embedding, content, article_number, title))
#         pg_conn.commit()
#         print("Documents inserted successfully.")
#     except Exception as e:
#         print(f"Error inserting documents into PostgreSQL: {e}")
#     finally:
#         if 'pg_cur' in locals() and pg_cur:
#             pg_cur.close()


from typing import Dict, List, Sequence
import psycopg2
from psycopg2 import sql
from config.settings import PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB, PG_TABLE, PG_SCHEMA
from models.embeddings import generate_articles_with_embeddings, generate_embedding

def initialize_postgresql(reset, data_path, embedding_model, embedding_path):
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
                    
                    # Generate a sample embedding to determine its dimensionality
                    value_names = {
                        'article_number': "article_number",
                        'title': "title",
                        'content': "content",
                        'embedding': "embedding",
                    }
                    sample_embedding = generate_embedding("test sample", embedding_model, value_names)
                    if not sample_embedding:
                        raise ValueError("Failed to generate a sample embedding to determine vector dimensions.")
                    embedding_dim = len(sample_embedding)
                    print(f"Detected embedding dimensions: {embedding_dim}")

                    # Create the table with dynamic embedding dimensions
                    cur.execute(sql.SQL(
                        f"""
                        CREATE TABLE IF NOT EXISTS {PG_SCHEMA}.{PG_TABLE} (
                            id SERIAL PRIMARY KEY,
                            {value_names['article_number']} INT NOT NULL,
                            {value_names['title']} TEXT NOT NULL,
                            {value_names['content']} TEXT NOT NULL,
                            {value_names['embedding']} VECTOR({embedding_dim})
                        );
                        """
                    ))
                    
                    print(f"Schema '{PG_SCHEMA}' and table '{PG_TABLE}' initialized with vector dimensions {embedding_dim}.")
                    
                    # Process and insert embeddings
                    articles_with_embeddings = generate_articles_with_embeddings(
                        data_path=data_path, embedding_path=embedding_path, embedding_model=embedding_model, value_names=value_names
                    )
                    insert_articles_with_embeddings(conn=conn, articles_with_embeddings=articles_with_embeddings, table_name=PG_TABLE, schema_name=PG_SCHEMA, value_names=value_names)
            
        print("Postgres initialized.")
                    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except ValueError as ve:
        print(f"Initialization error: {ve}")

def insert_articles_with_embeddings(conn, articles_with_embeddings: List[Dict[str, Sequence[float]]], table_name: str, schema_name: str, value_names: List[str]):
    """
    Inserts articles and embeddings into PostgreSQL using pgvector.
    """
    if not conn:
        print("Invalid PostgreSQL connection. Skipping insertion.")
        return

    try:
        print(f"Inserting embeddings into PostgreSQL table '{schema_name}.{table_name}'...")
        with conn.cursor() as pg_cur:
            for article in articles_with_embeddings:
                # Insert into PostgreSQL
                pg_cur.execute(sql.SQL("""
                    INSERT INTO {}.{} ({}, {}, {}, {})
                    VALUES (%s::vector, %s, %s, %s);
                """).format(
                    sql.Identifier(schema_name),
                    sql.Identifier(table_name),
                    sql.Identifier(value_names['article_number']),
                    sql.Identifier(value_names['title']),
                    sql.Identifier(value_names['content']),
                    sql.Identifier(value_names['embedding']),
                ), (article.get(value_names['article_number']), article.get(value_names['title']), article.get(value_names['content']), article.get(value_names['embedding'])))
            conn.commit()
        print("Documents inserted successfully.")
    except Exception as e:
        print(f"Error inserting documents into PostgreSQL: {e}")