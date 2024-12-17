import os
from typing import Sequence
import ollama
import json
from typing import List, Dict


def generate_embedding(content: json, embedding_model: str) -> Sequence[float]:
    """
    Generate an embedding for the given text using the specified embedding model.
    """
    try:
        embeddings = ollama.embeddings(model=embedding_model, prompt=content)["embedding"]
        return embeddings
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return

def generate_articles_with_embeddings(data_path: str, embedding_path: str, embedding_model: str, value_names: Dict[str, str]) -> List[Dict[str, Sequence[float]]]:
    """
    Process structured articles, generate embeddings if needed, and return a list of articles with embeddings.
    """
    # Check if the embedding file exists and is not empty
    if os.path.exists(embedding_path) and os.path.getsize(embedding_path) > 0:
        with open(embedding_path, "r", encoding="utf-8") as file:
            articles_with_embeddings = json.load(file)
        return articles_with_embeddings

    # If the file does not exist or is empty, generate embeddings
    print(f"Embedding file not found or empty. Generating embeddings...")
    with open(data_path, "r", encoding="utf-8") as file:
        articles = json.load(file)

    articles_with_embeddings = []
    for article in articles:
        embedding = generate_embedding(content=article[value_names['content']], embedding_model=embedding_model)
        if embedding:
            articles_with_embeddings.append({
                value_names['article_number']: article[value_names['article_number']],
                value_names['title']: article[value_names['title']],
                value_names['content']: article[value_names['content']],
                value_names['refs']: article['references'],
                value_names['embedding']: embedding
            })

    # Save the generated embeddings to the file
    with open(embedding_path, "w", encoding="utf-8") as output_file:
        json.dump(articles_with_embeddings, output_file, ensure_ascii=False, indent=4)

    print(f"Embeddings saved to {embedding_path}")
    return articles_with_embeddings

