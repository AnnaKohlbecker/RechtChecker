import ollama
import json


def generate_embedding(text, embedding_model="mxbai-embed-large:latest"):
    """
    Generate an embedding for the given text using the specified embedding model.

    :param text: The input text to be embedded.
    :param embedding_model: The model to use for generating embeddings.
    :return: A list representing the text embedding.
    """
    try:
        return ollama.embeddings(model=embedding_model, prompt=text)["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def process_articles_with_embeddings(file_path, embedding_model="mxbai-embed-large:latest"):
    """
    Process structured articles, generate embeddings, and return a list of articles with embeddings.
    
    :param file_path: Path to the structured JSON file.
    :param embedding_model: The model to use for generating embeddings.
    :return: List of dictionaries containing 'content' and 'embedding'.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        articles = json.load(file)

    processed_articles = []
    for article in articles:
        embedding = generate_embedding(article["content"], embedding_model)
        if embedding:
            processed_articles.append({"content": article["content"], "embedding": embedding})

    return processed_articles
