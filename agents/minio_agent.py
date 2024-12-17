import db.minio as minio
from models.llm_client import LLMClient
from config.settings import LLM_MODEL


class MinIOAgent:
    def __init__(self):
        self.llm_client = LLMClient()
        self.session = minio.initialize_minio()


    def get_article_number(self, question: str) -> str:
        prompt_german = f"""
                Du bist ein Experte darin erwähnte Nummern aus Benutzerfragen zu entnehmen.
                Jede Benutzerfrage enthält genau **eine** Zahl, diese ist das **einzige**, was du zurück geben sollst.
                Dementsprechend besteht deine Antwort aus einem einzigen Integer-Wert.

                Vor der Zahl steht oft das Wort Artikel, darauf musst du besonders achten.

                Beispiele:
                    - "Gib mir Artikel 3 als PDF." -> 3
                    - "Lade Artikel 7 als PDF herunter." -> 7

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
            model=LLM_MODEL,
            messages=messages,
            max_tokens=10,
            temperature=0
        )
        return response["choices"][0]["message"]["content"].strip().lower()


    def handle_question(self, question: str) -> str:
        response = "Hier ist die angeforderte PDF."
        article_number = self.get_article_number(question)
        article_name = f"Artikel{article_number}"
        minio.get_article(self.session, article_name)
        return response