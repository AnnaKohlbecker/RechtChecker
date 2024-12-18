import json
import sys
from config.settings import LLM_MODEL
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
        
def start_rechtchecker(reset_dbs, clear_cache, question):
    manager_agent = ManagerAgent(reset_dbs=reset_dbs, clear_cache=clear_cache)
    return manager_agent.handle_question(question)
            
def main(): 
    response = {"message": "error"}
    try:
        if len(sys.argv) > 1:
            question = sys.argv[1]
        message = start_rechtchecker(reset_dbs=True, clear_cache=False, question=question)
        response.update({"message": message})
    except Exception as e:
        response.update({"message": json.dumps(str(e).replace('"', '\\"').replace('\n', '\\n'))})
    print(json.dumps(response))
    
if __name__ == "__main__":
    main()