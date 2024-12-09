import os
from config.settings import CHUNKED_DATA_PATH, RAW_DATA_PATH, STRUCTURED_DATA_PATH
from utils.docker_utils import start_docker
from utils.file_utils import chunk_text_delimiter, preprocess_articles

def initialize_docker_and_containers():
    print("\n*** Initialize Docker And Containers ***")
    start_docker()
    
def initialize_data():
    print("\n*** Initialize Data ***")
    delimiter = "GG Art"
    if not os.path.exists(CHUNKED_DATA_PATH):
        chunk_text_delimiter(input_path=RAW_DATA_PATH, output_path=CHUNKED_DATA_PATH, delimiter=delimiter)
    if not os.path.exists(STRUCTURED_DATA_PATH):
        preprocess_articles(input_path=CHUNKED_DATA_PATH, output_path=STRUCTURED_DATA_PATH)
    else:
        print("Data initialized.")