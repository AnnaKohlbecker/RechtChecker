import db.neo4j as neo4j
from models.llm_client import LLMClient


class Neo4jAgent:
    def __init__(self):
        self.llm_client = LLMClient()
        self.session = neo4j.initialize_neo4j()


    def get_article_number(self, question: str) -> str:
        prompt_german = f"""
                Du bist ein Experte darin erwähnte Nummern aus Benutzerfragen zu entnehmen.
                Jede Benutzerfrage enthält genau **eine** Zahl, diese ist das **einzige**, was du zurück geben sollst.
                Dementsprechend besteht deine Antwort aus einem einzigen Integer-Wert.

                Vor der Zahl steht oft das Wort Artikel, darauf musst du besonders achten.

                Beispiele:
                    - "Welche Artikel verweisen auf Artikel 3?" -> 3
                    - "Auf was verweist Artikel 7?" -> 7

                Für Fragen, die nicht dem oben definierten Muster entsprechen antworte mit "none".
                Beispiele:
                    - "Ist der Himmel blau?" -> none
                    - "Was ist ein Lichtjahr?" -> none

                Beantworte **NICHT** und auf **KEINEN** Fall die Benutzerfrage, sondern folge **ausschließlich** deiner Aufgabe.
                Wichtig ist auch: Antworte **nur** und wirklich **NUR** mit der Nummer und gebe keine zusätzlichen Erklärungen dazu.

                Benutzerfrage: "{question}"    
                """
        messages = [{"role": "user", "content": prompt_german}]
        response = self.llm_client.query_instruct(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=messages,
            max_tokens=10,
            temperature=0
        )
        return response["choices"][0]["message"]["content"].strip().lower()

    def handle_query(self, question: str) -> str:
        """
        Placeholder for Neo4j Agent query handling.

        Args:
            question (str): The user question.

        Returns:
            str: "Not Implemented"
        """
        article_number = self.get_article_number(question)

        return f"The requested article number is {article_number}"