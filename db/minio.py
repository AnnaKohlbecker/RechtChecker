import json
import os
import minio
from config.settings import MINIO_HOST, MINIO_PORT, MINIO_USER, MINIO_PASSWORD, DOWNLOAD_PATH, STRUCTURED_JSON_PATH
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


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
        get_article(client, article)
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
            get_article(client, article)
        else:
            print(f"Error on loading pdf: {e}.")


def get_article(client, article):
    directory = f"{DOWNLOAD_PATH}/{article}"
    try:
        client.stat_object("articles", article)
        client.fget_object("articles", article, directory)
        print(f"The PDF '{article}' has been downloaded successfully.")
    except minio.S3Error as e:
        if e.code == "NoSuchKey":


            create_pdf(client, article)
        else:
            print(f"Error on downloading PDF: {e}")


def create_pdf(client, article_name):
    output_file = f"./articles/{article_name}.pdf"
    article_number = article_name.split('l')[1]

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    c = canvas.Canvas(output_file, pagesize=A4)
    c.setFont("Helvetica", 12)
    width, height = A4
    x_margin = 50
    y_position = height - 50
    line_height = 14

    with open(STRUCTURED_JSON_PATH, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for article in data:
        if article['article_number'] == article_number:
            title_line = f"Artikel {article['article_number']} - {article['title']}"
            c.setFont("Helvetica-Bold", 14)
            c.drawString(x_margin, y_position, title_line)
            y_position -= (line_height * 2)

            c.setFont("Helvetica", 12)
            lines = article["content"].split('\n')
            for line in lines:
                if y_position < 50:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y_position = height - 50

                c.drawString(x_margin, y_position, line)
                y_position -= line_height
            c.save()
            insert_article(client, output_file)
            break