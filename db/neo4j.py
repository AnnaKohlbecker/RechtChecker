import json
from config.settings import NEO4J_HOST, NEO4J_PORT, NEO4J_PASSWORD, NEO4J_USER, STRUCTURED_JSON_PATH
import neo4j


def initialize_neo4j():
    try:
        print("Initializing Neo4j...")
        uri = f"bolt://{NEO4J_HOST}:{NEO4J_PORT}"
        auth = (NEO4J_USER, NEO4J_PASSWORD)
        driver = neo4j.GraphDatabase.driver(uri, auth=auth)
        driver.verify_connectivity()
        print("Neo4j initialized successfully.")

        data = ""
        with open(STRUCTURED_JSON_PATH, 'r', encoding='utf-8') as file:
            data =  json.load(file)

        insert_data(driver.session(), data)
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
    MERGE (a:Article {article_number: article.article_number})
    SET a.title = article.title,
        a.content = article.content
    """
    session.run(query, articles=articles)


# Creates the relationships based on references
def create_references(session, articles):
    query = """
    UNWIND $articles AS article
    MATCH (a:Article {article_number: article.article_number})
    UNWIND article.references AS ref
    MATCH (refArticle:Article {article_number: ref})
    MERGE (a)-[:REFERENCES]->(refArticle)
    """
    session.run(query, articles=articles)


def get_referenced_articles(session, article_number):
    query = """
    MATCH (a:Article {article_number: $article_number})-[:REFERENCES]->(referenced:Article)
    RETURN referenced.article_number AS referenced_number
    """
    result = session.run(query, article_number=str(article_number))
    return [record["referenced_number"] for record in result]


def get_articles_referencing(session, article_number):
    query = """
    MATCH (referencing:Article)-[:REFERENCES]->(a:Article {article_number: $article_number})
    RETURN referencing.article_number AS referencing_number
    """
    result = session.run(query, article_number=str(article_number))
    return [record["referencing_number"] for record in result]