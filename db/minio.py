import os
import minio
from config.settings import MINIO_HOST, MINIO_PORT, MINIO_USER, MINIO_PASSWORD

def initialize_minio():
    try:
        uri = f"{MINIO_HOST}:{MINIO_PORT}"
        client = minio.Minio(
            uri,
            access_key=MINIO_USER,
            secret_key=MINIO_PASSWORD,
            secure=False
        )
        create_bucket(client)

        print("MinIO initialized.")
        return client
    except Exception as e:
        print(f"Error initializing MinIO: {e}")
        return None

def create_bucket(client):
    bucket_name = "articles"
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)


def insert_article(client, path):
    article = os.path.basename(path)

    try:
        stat = client.stat_object("articles", article)
        print(f"The PDF '{article}' allready exists in bucket 'articles'.")
    except minio.S3Error as e:
        if e.code == "NoSuchKey":
            file_size = os.path.getsize(path)
            with open(path, "rb") as f_data:
                client.put_object(
                    "articles",
                    article,
                    f_data,
                    file_size,
                    content_type="application/pdf"
                )
            print(f"The PDF '{article}' has been uploaded into bucket 'articles' successfully.")
        else:
            print(f"Error on loading pdf: {e}.")


def get_article(client, article):
    try:
        client.stat_object("articles", article)

        client.fget_object("articles", article, article)
        print(f"The PDF '{article}' has been downloaded successfully.")
    except minio.S3Error as e:
        if e.code == "NoSuchKey":
            print(f"The PDF '{article}' does not exist in bucket 'articles'.")
        else:
            print(f"Error on downloading PDF: {e}")