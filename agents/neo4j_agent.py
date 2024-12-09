from config.settings import LLM_MODEL
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
            model=LLM_MODEL,
            messages=messages,
            max_tokens=10,
            temperature=0
        )
        return response["choices"][0]["message"]["content"].strip().lower()


    def get_question_type(self, question: str) -> str:
        """
        returns one of the following question types:

            - referenced_articles
            - referencing_articles
            - none
        """
        prompt_german = f"""
        Du bist ein Experte in der Kategorisierung von Anfragen, die mit Artikelverweisen zu tun haben.
        Deine Aufgabe ist es, Benutzerfragen in eine der folgenden Kategorien einzuordnen. 
        Bitte beachte, dass sich die Kategorien sehr ähnlich sind, du musst dir bei deiner Antwort also sehr sicher sein.
        Jede Frage gehört genau einer Kategorie. Jede Frage muss genau und nur eine Kategorie bekommen:

        - **referenced_articles**: Für Fragen darüber, auf welche Artikel der gegebene Artikel verweist. Achte besonders auf derartige Formulierungen:
        - "Auf welche Artikel verweist Artikel X?"
        - "Von welchen Artikeln hängt Artikel X ab?"
        - "Welche Artikeln werden im Artikel X referenziert?"
        Beispiele:
            - "Auf welche Artikel verweist Artikel 9?" -> referenced_articles
            - "Welche Artikel werden im Artikel 13 referenziert?" -> referenced_articles
            - "Auf welche Artikel verweist Artikel 12?" -> referenced_articles       
            - "Von welchen Artikeln hängt Artikel 15 ab?" -> referenced_articles
        
        - **referencing_articles**: Für Fragen darüber, welche Artikel auf den gegebenen Artikel veweisen. Achte besonders auf derartige Formulierungen:
        - "Welche Artikel verweisen auf Artikel X?"
        - "Welche Artikel stellen eine Verbindung zu Artikel X her?"
        - "Welche Artikel nehmen Bezug auf Artikel X?"
        - "Welche Verweise gibt es auf Artikel X?"
        - "Welche Artikel sind mit Artikel X verknüpft?"
        - "Gibt es Artikel, die auf Artikel X Bezug nehmen?"
        Beispiele:
            - "Welche Artikel verweisen auf Artikel 7?" -> referencing_articles
            - "Welche Artikel verweisen auf Artikel 12?" -> referencing_articles
            - "Welche Verweise gibt es auf Artikel 1?" -> referencing_articles
            - "Im Grundgesetz, welche Verweise gibt es auf Artikel 2?" -> referencing_articles
            - "Welche Artikel nehmen Bezug auf Artikel 60?" -> referencing_articles
            - "Welche Artikel stellen eine Verbindung zu Artikel 30 her?" -> referencing_articles
            - "Gibt es Artikel, die auf Artikel 20 Bezug nehmen?" -> referencing_articles
            - "Welche Verweise gibt es auf Artikel 1 des Grundgesetzes?" -> referencing_articles

        - **"none"**: Für Fragen, die nicht mit den oben genannten Kategorien oder dem Grundgesetz zusammenhängen, wie z. B. persönliche oder irrelevante Fragen. 
        - Also allgemein für Fragen, die nichts mit Referenzierungen zwischen Grundgesetzartikeln zu tun haben.
        - Auch für Fragen, wo du dir nicht sicher bist, welche Kategorie dazu passt. Beispiele:
        - "Wie heißt mein Hund?" -> none
        - "Was ist das Wetter morgen?" -> none
        - "Wie groß ist die Erde?" -> none
        - "Was ist die Hauptstadt von Frankreich?" -> none

        Antworte **nur** und wirklich **NUR** mit dem Kategoriennamen. Deine Ausgabe darf also nur so aussehen:
        - referenced_articles
        - referencing_articles
        - none
        
        Wenn du dir nicht sicher bist, antworte lieber mit none.
        
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
        response = ""
        article_number = self.get_article_number(question)
        question_type = self.get_question_type(question)
        articles = []

        match question_type:
            case "referenced_articles":
                response += f"Folgende Artikel werden von Artikel {article_number} referenziert:\n"
                articles = neo4j.get_referenced_articles(self.session, article_number)
            case "referencing_articles":
                response += f"Folgende Artikel referenzieren Artikel {article_number}:\n"
                articles = neo4j.get_articles_referencing(self.session, article_number)
            case "none":
                return "Entschuldigung, diese Frage gehört nicht zu meinem Anwendungsbereich."

            case _:
                return "Entschuldigung, ich konnte Ihre Frage nicht verstehen."

        if len(articles) == 0:
            return response + "Keine Artikel gefunden."

        for article in articles:
            response += (
                f"Artikel {article['article_number']}:\n"
                f"{article['content']}\n\n"
            )

        return response