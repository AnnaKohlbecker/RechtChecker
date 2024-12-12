from config.settings import LLM_MODEL
from initialization import initialize_data, initialize_docker_and_containers
from agents.manager_agent import ManagerAgent

def test_instruct_model(llm_client, query):
    try:
        instruct_model_name = LLM_MODEL
        messages = [{"role": "user", "content": query}]
        instruct_response = llm_client.query_instruct(
            model=instruct_model_name,
            messages=messages,
            max_tokens=512,
            temperature=0.0
        )        
        print("Instruct Model Response:", instruct_response["choices"][0]["message"]["content"])
    except RuntimeError as e:
        print(e)
        
def test_chat_model(llm_client, query):
    try:
        chat_model_url = f"https://api-inference.huggingface.co/models/{LLM_MODEL}"
        chat_response = llm_client.query_chat(
            model_url=chat_model_url,
            inputs=query,
            max_tokens=100,
            temperature=0.1
        )        
        print("Chat Model Response:", chat_response)
    except RuntimeError as e:
        print(e)
        
def start_rechtchecker(reset_dbs, clear_cache):
    print("\n*** Start Rechtchecker ***")
    manager_agent = ManagerAgent(reset_dbs=reset_dbs, clear_cache=clear_cache)
    
    german_questions = [
        # Neo4j
         "Welche Artikel werden im Artikel 13 referenziert?",
         "Gibt es Artikel auf die Artikel 12 referenziert?",
        # "Welche Artikel verweisen auf Artikel 14?",
        # "Welche Artikel sind mit Artikel 3 verknüpft?",
         "Gibt es Artikel, die auf Artikel 15 Bezug nehmen?",
         "Welche Artikel sind mit Artikel 100 verknüpft?",
        # "Welche Verweise gibt es auf Artikel 3 des Grundgesetzes?",
        # "Kannst du mir zeigen, welche Artikel Bezug auf Artikel 13 nehmen?",

        # # MongoDB
         "Was versteht man unter Artikel 16?",
         "Erkläre mir Artikel 5 des Grundgesetzes.",
        # "Fass Artikel 10 aus dem Grundgesetz zusammen.",
        # "Was bedeutet Artikel 11 im Grundgesetz?",
         "Erkläre den Inhalt von Artikel 13.",
        # "Kannst du mir eine kurze Zusammenfassung von Artikel 4 geben?",

        # # MinIO
        # "Gib mir Artikel 3 als PDF.",
        # "Lade Artikel 7 als PDF herunter.",
        # "Zeig mir Artikel 15 als PDF.",
        # "Kannst du Artikel 18 als PDF bereitstellen?",
        # "Ich brauche Artikel 6 in einer PDF-Datei.",
        # "Gibt es Artikel 9 in PDF-Form?",

        # Postgres
        "Mein Arbeitgeber verlangt Überstunden, die ich nicht leisten möchte. Welche Rechte habe ich?",
        "Ich werde wegen meiner Religion benachteiligt. Was sagt das Grundgesetz dazu?",
        "Mein Chef verlangt von mir, gegen meine moralischen Überzeugungen zu handeln. Was kann ich tun?",
        # "Darf mein Arbeitgeber mich ohne Vorwarnung entlassen?",
        # "Mein Arbeitgeber überprüft meine privaten Nachrichten. Ist das erlaubt?",
        # "Ein Kollege verbreitet Unwahrheiten über mich. Kann ich mich rechtlich dagegen wehren?",

        # None
        "Was ist das Wetter morgen in Paris?",
        "Wie heißt die Mutter von Kevin?",
        "Wie alt bist du?",
        "Balabalabalabalabalba?",
        # "No",
        # "Wie viele Kilometer sind es von Berlin nach München?",
        # "Wann wurde das erste Auto erfunden?",
        # "Kannst du mir ein Rezept für Apfelkuchen geben?",
    
        # # Redis
        # "Ich werde auf der Arbeit gezwungen etwas zu tun, was ich nicht möchte. Habe ich Recht?",
        # "Mein Chef will mich ohne Grund feuern. Was kann ich tun?",
        # "Ich wurde auf der Arbeit beleidigt. Was sind meine Rechte?",
        # "Darf mein Arbeitgeber mich ohne Vorwarnung entlassen?",
        # "Ich fühle mich in meiner Nachbarschaft diskriminiert. Was kann ich tun?",
        # "Welche Rechte habe ich, wenn ich in der Öffentlichkeit gefilmt werde?",
    ]
    
    # english_questions = [
    #     # Neo4j
    #     "Which articles refer to Article 12?",
    #     "Which articles are linked to Article 8?",
    #     "Are there any articles that reference Article 20?",
    #     "Which articles are connected to Article 14?",
    #     "What references exist to Article 1 of the Basic Law?",
    #     "Can you show me which articles refer to Article 19?",

    #     # MongoDB
    #     "What does Article 16 mean?",
    #     "Explain Article 5 of the Basic Law to me.",
    #     "Summarize Article 10 of the Basic Law.",
    #     "What is the meaning of Article 11 in the Basic Law?",
    #     "Explain the content of Article 13.",
    #     "Can you give me a brief summary of Article 4?",

    #     # MinIO
    #     "Give me Article 3 as a PDF.",
    #     "Download Article 7 as a PDF.",
    #     "Show me Article 15 as a PDF.",
    #     "Can you provide Article 18 as a PDF?",
    #     "I need Article 6 in a PDF file.",
    #     "Is Article 9 available in PDF format?",

    #     # Postgres
    #     "I am being forced to do something at work that I don’t want to do. Do I have rights?",
    #     "My boss wants to fire me without reason. What can I do?",
    #     "I was insulted at work. What are my rights?",
    #     "Can my employer fire me without prior warning?",
    #     "I feel discriminated against in my neighborhood. What can I do?",
    #     "What are my rights if I am filmed in public?",
        
    #     # Redis
    #     "I am being forced to do something at work that I don’t want to do. Do I have rights?",
    #     "My boss wants to fire me without reason. What can I do?",
    #     "I was insulted at work. What are my rights?",
    #     "Can my employer fire me without prior warning?",
    #     "I feel discriminated against in my neighborhood. What can I do?",
    #     "What are my rights if I am filmed in public?",

    #     # None
    #     "What’s the weather in Paris tomorrow?",
    #     "What is Kevin’s mother’s name?",
    #     "How old are you?",
    #     "Balabalabalabalabalba?",
    #     "No",
    #     "How many kilometers is it from Berlin to Munich?",
    #     "When was the first car invented?",
    #     "Can you give me a recipe for apple pie?",
    # ]

    questions = german_questions

    # Process each question
    for question in questions:
        print(f"\n\n***Question***: {question}")
        response = manager_agent.handle_question(question)
        print(f"\n***Response***: {response}")
            
def main(): 
    initialize_docker_and_containers()
    initialize_data()
    try:
        start_rechtchecker(reset_dbs=True, clear_cache=True)
    except AttributeError:
        print("\n\n\nAn error occurred while starting Rechtchecker. Run 'main.py' again.")
    
if __name__ == "__main__":
    main()