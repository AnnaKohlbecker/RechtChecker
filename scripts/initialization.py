import os
import json
from config.settings import CHUNKED_DATA_PATH, RAW_DATA_PATH, STRUCTURED_DATA_PATH
from utils.docker_utils import start_docker
from utils.file_utils import chunk_text_delimiter, preprocess_articles

def initialize_docker_and_containers():
    """
    Starts Docker containers and returns a status message.
    """
    try:
        start_docker()
        return {"docker_status": "initialized"}
    except Exception as e:
        return {"docker_status": "failed", "error": str(e)}

def initialize_data():
    """
    Initializes data by chunking and preprocessing articles.
    Returns a status message.
    """
    try:
        delimiter = "GG Art"
        if not os.path.exists(CHUNKED_DATA_PATH):
            chunk_text_delimiter(input_path=RAW_DATA_PATH, output_path=CHUNKED_DATA_PATH, delimiter=delimiter)
        
        if not os.path.exists(STRUCTURED_DATA_PATH):
            preprocess_articles(input_path=CHUNKED_DATA_PATH, output_path=STRUCTURED_DATA_PATH)
        return {"data_status": "initialized"}
    except Exception as e:
        return {"data_status": "failed", "error": str(e)}

def main():
    response = {}
    response.update(initialize_docker_and_containers())
    response.update(initialize_data())
    response["status"] = "success" if "failed" not in response.values() else "failed"
    response["value"] = 42
    print(json.dumps(response))

if __name__ == "__main__":
    main()
