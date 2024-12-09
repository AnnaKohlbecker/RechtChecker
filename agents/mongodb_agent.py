import db.mongodb as mongodb
from models.llm_client import LLMClient

class MongoDBAgent:
    def __init__(self):
        """
        Initialize the MongoDBAgent with MongoDB connection, LLM client, and load data.
        """
        self.db = mongodb.initialize_mongodb()
        self.llm_client = LLMClient()
        
        # Ensure data is loaded into MongoDB
        if self.db != None:
            mongodb.insert_data(self.db)
            mongodb.create_index(self.db)  # Create index after loading data


    def get_article_number(self, question: str) -> str:
        """
        Extract the article number from the user question using LLM.

        Args:
            question (str): The user question.

        Returns:
            str: Extracted article number or "none" if not found.
        """
        prompt_german = f"""
        Du bist ein Experte für die Analyse von Benutzerfragen und darauf spezialisiert, die erwähnte Artikelnummer präzise zu extrahieren.
        Deine Aufgabe besteht ausschließlich darin, die Artikelnummer aus der Frage zu extrahieren. Beachte dabei folgende Regeln:

        1. Wenn die Frage eine Artikelnummer enthält, gib nur diese Zahl zurück.
        - Die Artikelnummer steht meist nach dem Wort "Artikel".
        - Die Antwort muss genau aus dieser Zahl bestehen, ohne zusätzliche Zeichen oder Wörter.
        2. Wenn keine Artikelnummer in der Frage vorkommt, antworte mit "none".
        3. Gib keine zusätzlichen Informationen oder Erklärungen. Deine Antwort ist immer nur:
        - Die Artikelnummer (z. B. "3").
        - Oder "none", wenn keine Artikelnummer gefunden wurde.

        Beispiele:
        - "Was besagt Artikel 3?" -> 3
        - "Kannst du mir Artikel 7 erklären?" -> 7
        - "Gibt es Informationen zu Artikel 42?" -> 42
        - "Was ist ein Lichtjahr?" -> none
        - "Erkläre mir bitte Artikel 10." -> 10
        - "Wie groß ist die Erde?" -> none

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
        Handle the query by fetching and explaining the relevant article using the LLM.

        Args:
            question (str): The user question.

        Returns:
            str: A generated response to the user query based on the article content or an error message.
        """
        # Step 1: Extract article number from the question
        article_number = self.get_article_number(question)
        if article_number == "none":
            return "Entschuldigung, ich konnte die Artikelnummer aus Ihrer Frage nicht extrahieren."

        # Step 2: Fetch the article from MongoDB
        article = mongodb.fetch_article(self.db, article_number)
        if not article:
            return f"Artikel {article_number} wurde nicht gefunden."

        # Step 3: Generate a response to the user's question using the LLM
        prompt = f"""
        Du bist ein Experte für das Grundgesetz und hilfst dabei, Benutzerfragen zu beantworten. 
        Der Benutzer hat eine Frage gestellt, die sich auf einen Artikel des Grundgesetzes bezieht. 
        Hier ist der Artikeltext:

        Artikel {article['article_number']}: {article['title']}
        {article['content']}

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
        )

        # Step 4: Return the generated response
        return response["choices"][0]["message"]["content"].strip()
