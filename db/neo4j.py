import json
from config.settings import NEO4J_HOST, NEO4J_PORT, NEO4J_PASSWORD, NEO4J_USER
import neo4j


def initialize_neo4j():
    try:
        print("Initializing Neo4j...")
        uri = f"bolt://{NEO4J_HOST}:{NEO4J_PORT}"
        auth = (NEO4J_USER, NEO4J_PASSWORD)
        driver = neo4j.GraphDatabase.driver(uri, auth=auth)
        driver.verify_connectivity()
        print("Neo4j initialized successfully.")
        return driver.session()
    except Exception as e:
        print(f"Error initializing Neo4j: {e}")
        return None


def insert_data(session, data):
    session.write_transaction(create_articles, data)
    session.write_transaction(create_references, data)


# Creates a node for each article.
def create_articles(session, articles):
    query = """
    UNWIND $articles AS article
    CREATE (a:Article {
        article_number: article.article_number,
        title: article.title,
        content: article.content
    })
    """
    session.run(query, articles=articles)


# Creates the relationships based on references
def create_references(session, articles):
    query = """
    UNWIND $articles AS article
    MATCH (a:Article {article_number: article.article_number})
    UNWIND article.references AS ref
    MATCH (refArticle:Article {article_number: ref})
    CREATE (a)-[:REFERENCES]->(refArticle)
    """
    session.run(query, articles=articles)