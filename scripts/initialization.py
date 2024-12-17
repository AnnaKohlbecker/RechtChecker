import os
import json
from config.settings import CHUNKED_DATA_PATH, RAW_DATA_PATH, STRUCTURED_DATA_PATH
from utils.docker_utils import start_docker
from utils.file_utils import chunk_text_delimiter, preprocess_articles

def main():
    response = {}
    
    try:
        start_docker()
        delimiter = "GG Art"
        if not os.path.exists(CHUNKED_DATA_PATH):
            chunk_text_delimiter(input_path=RAW_DATA_PATH, output_path=CHUNKED_DATA_PATH, delimiter=delimiter)
        if not os.path.exists(STRUCTURED_DATA_PATH):
            preprocess_articles(input_path=CHUNKED_DATA_PATH, output_path=STRUCTURED_DATA_PATH)
        response.update({"docker_and_data_status": "initialized"})
    except Exception as e:
        response.update({"docker_and_data_status": "failed", "error": str(e)})
    
    response["docker_and_data_status"] = "success" if "failed" not in response.values() else "failed"
    response["value"] = 42
    print(json.dumps(response))

if __name__ == "__main__":
    main()
