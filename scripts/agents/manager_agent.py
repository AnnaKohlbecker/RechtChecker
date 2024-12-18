from config.settings import LLM_MODEL
from models.llm_client import LLMClient
from agents.redis_agent import RedisAgent
from agents.neo4j_agent import Neo4jAgent
from agents.mongodb_agent import MongoDBAgent
from agents.minio_agent import MinIOAgent
from agents.postgres_agent import PostgresAgent
import json

class ManagerAgent:
    def __init__(self, reset_dbs, clear_cache):
        """
        Initialize the Manager Agent with all sub-agents.
        """
        self.llm_client = LLMClient()  # Uses the instruct model
        self.redis_agent = RedisAgent(clear_cache=clear_cache)
        self.neo4j_agent = Neo4jAgent(reset=reset_dbs)
        self.mongodb_agent = MongoDBAgent()
        self.minio_agent = MinIOAgent()
        self.postgres_agent = PostgresAgent(reset=reset_dbs)

    def classify_question(self, question: str) -> str:
        """
        Classify the user question into predefined categories using the LLM instruct model.

        Args:
            question (str): The user question.

        Returns:
            str: The category of the question.
        """
        
        prompt_english = f"""
        You are an expert Manager Agent. Your task is to classify user questions into one of the following categories. 
        Each question must belong to exactly one category. Each question must receive precisely and only one category:

        - **"neo4j"**: For questions about **references** or **relationships** between articles in a knowledge graph. Look for phrases like:
        - "Which articles refer to..."
        - "Which articles are linked to Article X?"
        Examples:
            - "Which articles refer to Article 9?" -> neo4j
            - "Which articles refer to Article 12?" -> neo4j

        - **"mongodb"**: For requests for **summarization**, **explanation**, or **interpretation** of a specific article. These questions directly ask for the meaning or an overview of an article. Look for phrases like:
        - "What does Article X state?"
        - "Summarize Article X for me."
        Examples:
            - "What does Article 16 mean?" -> mongodb
            - "Summarize Article 124 from the Basic Law for me." -> mongodb

        - **"minio"**: For requests for **PDF documents**. Look for phrases like:
        - "Give me Article X as a PDF."
        - "Show me the PDF version of Article X."
        Examples:
            - "Give me Article 3 as a PDF." -> minio
            - "Download Article 7 as a PDF for me." -> minio

        - **"postgres"**: For questions about **general legal advice** or the interpretation of rights that are not related to specific articles. These questions often describe scenarios and ask for legal clarification. Look for phrases like:
        - "Do I have the right to..."
        - "What are my rights?"
        Examples:
            - "I am being forced to do something at work that I don’t want to. Do I have the right?" -> postgres
            - "I was laughed at in school yesterday. What are my rights?" -> postgres

        - **"none"**: For questions that are not related to the above categories or the Basic Law. 
        - In general, for questions that have nothing to do with the Basic Law or any rights or articles from the Basic Law. 
        - Also for questions where you are unsure which category applies. Examples:
            - "What is my dog’s name?" -> none
            - "What’s the weather tomorrow?" -> none
            - "How big is the Earth?" -> none
            - "What is the capital of France?" -> none

        Respond **only** and truly **ONLY** with the category name in the following JSON format:
        {{"classification": "<category_name>"}}

        User Question: "{question}"
        """   
        
        prompt_german = f"""
        Du bist ein Experten-Manager-Agent. Deine Aufgabe ist es, Benutzerfragen in eine der folgenden Kategorien einzuordnen. 
        Jede Frage gehört genau einer Kategorie. Jede Frage muss genau und nur eine Kategorie bekommen:

        - **"neo4j"**: Für Fragen über **Verweise** oder **Beziehungen** zwischen Artikeln in einem Wissensgraphen. Achte auf Phrasen wie:
        - "Welche Artikel verweisen auf..."
        - "Welche Artikel sind mit Artikel X verknüpft?"
        Beispiele:
            - "Welche Artikel verweisen auf Artikel 9?" -> neo4j
            - "Welche Artikel verweisen auf Artikel 12?" -> neo4j

        - **"mongodb"**: Für Anfragen zur **Zusammenfassung**, **Erklärung**, **Bedeutung** oder **Interpretation** eines bestimmten Artikels. 
        Diese Fragen fragen direkt nach der Bedeutung oder einem Überblick über einen Artikel. Achte auf Phrasen wie:
        - "Was besagt Artikel X?"
        - "Fass mir bitte Artikel X zusammen."
        - "Was steht im Artikel X drin?"
        - "Was bedeutet Artikel X?"
        - "Erkläre mir Artikel X."
        Beispiele:
            - "Was versteht man unter Artikel 16?" -> mongodb
            - "Fass mir bitte Artikel 124 aus dem Grundgesetz zusammen." -> mongodb
            - "Erkläre mir Artikel 5 des Grundgesetzes." -> mongodb
            - "Was bedeutet Artikel 11 im Grundgesetz?" -> mongodb
            - "Erkläre den Inhalt von Artikel 13." -> mongodb
            - "Kannst du mir eine kurze Zusammenfassung von Artikel 4 geben?" -> mongodb


        - **"minio"**: Für Anfragen nach **PDF-Dokumenten**. Achte auf Phrasen wie:
        - "Gib mir Artikel X als PDF."
        - "Zeig mir die PDF-Version von Artikel X."
        Beispiele:
            - "Gib mir Artikel 3 als PDF." -> minio
            - "Lade Artikel 7 als PDF herunter." -> minio

        - **"postgres"**: Für Fragen nach **allgemeiner rechtlicher Beratung** oder der Interpretation von Rechten, die sich nicht auf bestimmte Artikel beziehen. 
        Diese Fragen beschreiben oft Szenarien und fragen nach rechtlicher Klärung. 
        WICHTIG: **Fragen nach Zusammenfassungen, Erklärungen, Bedeutungen usw. sind nicht teil von postgres, sondern mongodb.**
        Achte auf Phrasen wie:
        - "Habe ich das Recht, ..."
        - "Was sind meine Rechte?"
        Beispiele:
            - "Ich werde auf der Arbeit gezwungen etwas zu tun, was ich nicht möchte. Habe ich Recht?" -> postgres
            - "Ich wurde gestern in der Schule ausgelacht. Was sind meine Rechte?" -> postgres

        - **"none"**: Für Fragen, die nicht mit den oben genannten Kategorien oder dem Grundgesetz zusammenhängen, wie z. B. persönliche oder irrelevante Fragen. 
        - Also allgemein für Fragen, die nichts mit dem Grundgesetz zu tun haben oder irgendwelche Rechte oder Artikeln aus dem Grundgesetz. 
        - Auch für Fragen, wo du dir nicht sicher bist, welche Kategorie dazu passt. Beispiele:
        - "Wie heißt mein Hund?" -> none
        - "Was ist das Wetter morgen?" -> none
        - "Wie groß ist die Erde?" -> none
        - "Was ist die Hauptstadt von Frankreich?" -> none

        Antworte **nur** und wirklich **NUR** mit dem Kategoriennamen im folgenden JSON-Format:
        {{"classification": "<category_name>"}}

        Benutzerfrage: "{question}"
        """
        
        messages = [{"role": "user", "content": prompt_german}]
        response = self.llm_client.query_instruct(
            model=LLM_MODEL,
            messages=messages,
            max_tokens=50,
            temperature=0
        )
        return response["choices"][0]["message"]["content"].strip()

    def handle_question(self, question: str) -> str:
        """
        Direct the question to the appropriate agent based on its classification.

        Args:
            question (str): The user question.

        Returns:
            str: The answer from the appropriate agent.
        """
        # Step 1: Check Redis Cache
        uniform_question = question.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        cached_response = self.redis_agent.check_cache(uniform_question)
        if cached_response is not None:
            return f"Redis: {cached_response}"
        
        else:
            # Step 2: Classify the Question
            
            classification_response = self.classify_question(question)  # Returns {"classification": "<category_name>"}
            classification = ""
            try:
                classification_data = json.loads(classification_response)
                classification = classification_data.get("classification")
            except json.JSONDecodeError:
                return "Entschuldigung, ich konnte Ihre Frage nicht verstehen."  # Handle invalid JSON response

            # Step 3: Route to Appropriate Agent
            response_agent = ""
            match classification:
                case "neo4j":
                    response_agent = "Neo4J: "
                    response = self.neo4j_agent.handle_question(question)
                case "mongodb":
                    response_agent = "MongoDB: "
                    response = self.mongodb_agent.handle_question(question)
                case "minio":
                    response_agent = "MinIO: "
                    response = self.minio_agent.handle_question(question)
                case "postgres":
                    response_agent = "PostgreSQL: "
                    response = self.postgres_agent.handle_question(question)
                case "none":
                    response = "Entschuldigung, diese Frage gehört nicht zu meinem Anwendungsbereich."
                case _:
                    response = "Entschuldigung, ich konnte Ihre Frage nicht verstehen."

            uniform_response = response.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
            self.redis_agent.store_cache(uniform_question, uniform_response)
            
            response = response_agent + response
            
            return response