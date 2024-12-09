import psycopg2
from psycopg2 import sql
from config.settings import EMBEDDING_MODEL, PG_TABLE, PG_SCHEMA, RESET_DBS
from db.postgres import initialize_postgresql
from models.embeddings import generate_embedding
from models.llm_client import LLMClient

class PostgresAgent:
    def __init__(self, reset):
        """
        Initialize the Postgres Agent with a connection to the PostgreSQL database.
        """
        self.llm_client = LLMClient()
        self.conn = initialize_postgresql(reset=reset)

    def find_similar(self, question_embedding, top_n=1):
        """
        Find the most similar articles to the given question embedding.

        Args:
            question_embedding (list[float]): The embedding of the user's question.
            top_n (int): The number of top similar results to return.

        Returns:
            str: The most similar articles' content.
        """
        try:
            with self.conn.cursor() as cur:
                # SQL query to find the most similar vectors
                query = sql.SQL(f"""
                    SELECT content, title, article_number, 1 - (embedding <=> %s::vector) AS similarity
                    FROM {PG_SCHEMA}.{PG_TABLE}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s;
                """)
                cur.execute(query, (question_embedding, question_embedding, top_n))
                results = cur.fetchall()

                if not results:
                    return "No similar articles found."
                
                # Format the results into a readable response
                response = "\n".join(
                    [f"Article {row[2]}: {row[1]} (Similarity: {row[3]:.2f})\n{row[0]}" for row in results]
                )
                return response

        except Exception as e:
            return f"Error querying PostgreSQL: {e}"

    def handle_question(self, question: str) -> str:
        """
        Handle the user's query by generating its embedding and finding the most similar content.

        Args:
            question (str): The user's question.

        Returns:
            str: The answer based on the most similar content in the database.
        """
        try:
            # Generate the embedding for the user's question
            question_embedding = generate_embedding(content=question, embedding_model=EMBEDDING_MODEL)

            if not question_embedding:
                return "Could not generate embedding for the question."

            # Find the most similar articles
            response = self.find_similar(question_embedding, top_n=3)
            
            # Modify the response to match the users question
            prompt = f"""
            Du bist ein Experte für das Grundgesetz und hilfst dabei, Benutzerfragen zu beantworten. 
            Der Benutzer hat eine Frage gestellt, die sich auf einen Artikel des Grundgesetzes bezieht. 
            Hier ist der Artikeltext:
            {response}
            
            Bitte beantworte die folgende Benutzerfrage auf Grundlage dieses Artikels:
            
            Benutzerfrage: "{question}"
            
            Deine Antwort sollte klar und präzise sein und sich nur auf den gegebenen Artikeltext beziehen.
            """
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_client.query_instruct(
                model="meta-llama/Llama-3.2-1B-Instruct",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )["choices"][0]["message"]["content"].strip()
            
            return response

        except Exception as e:
            return f"Error handling query: {e}"
