import json
import os
import re

def chunk_text_delimiter(file_path, output_path, delimiter="GG Art"):
    """
    Splits the text from the input file into chunks based on the specified delimiter and saves the chunks to a JSON file.
    
    :param file_path: Path to the input text file.
    :param output_path: Path to save the resulting chunks as a JSON file.
    :param delimiter: Delimiter string used to split the text.
    """
    # Check if the output file already exists
    if os.path.exists(output_path):
        print(f"Output file '{output_path}' already exists. Skipping chunking.")
        return

    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split content into chunks
    chunks = content.split(delimiter)
    processed_chunks = [f"{delimiter}{chunk.strip()}" for chunk in chunks[1:]]

    # Write the chunks to the output file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(processed_chunks, output_file, ensure_ascii=False, indent=4)

    print(f"Chunking complete! {len(processed_chunks)} chunks saved to {output_path}")

def preprocess_articles(input_path, output_path):
    """
    Processes the chunked articles into a structured format with metadata fields and extracts references.

    :param input_path: Path to the JSON file containing chunked articles.
    :param output_path: Path to save the structured JSON file.
    """
    # Read the chunked data
    with open(input_path, 'r', encoding='utf-8') as file:
        chunks = json.load(file)

    articles = []

    # Regular expressions for reference patterns
    reference_patterns = {
        "artikel": re.compile(r"Artikel\s(\d+[a-z]?)"),
        "artikels": re.compile(r"Artikels\s(\d+[a-z]?)"),
        "artikeln": re.compile(r"Artikeln\s((?:\d+[a-z]?(?:,\s*)?)+)")
    }

    for chunk in chunks:
        # Extract article number and title
        lines = chunk.split("\n")
        first_line = lines[0].strip()
        
        # Match article number
        article_match = re.match(r"GG Art(\d+[a-z]?)", first_line)
        article_number = article_match.group(1) if article_match else None

        # Remaining text as content
        title = first_line.split(maxsplit=1)[-1] if " " in first_line else "No Title"
        content = "\n".join(lines[1:]).strip()

        # Extract references
        references = set()

        # Match "Artikel" and "Artikels"
        for key in ["artikel", "artikels"]:
            references.update(match.group(1) for match in reference_patterns[key].finditer(content))

        # Match "Artikeln" with multiple references
        artikeln_match = reference_patterns["artikeln"].search(content)
        if artikeln_match:
            multiple_references = artikeln_match.group(1)
            references.update(ref.strip() for ref in multiple_references.split(","))

        # Add structured data
        articles.append({
            "article_number": article_number,
            "title": title,
            "content": content,
            "references": list(references)
        })

    # Write the structured data to the output file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(articles, output_file, ensure_ascii=False, indent=4)

    print(f"Preprocessing complete! {len(articles)} articles saved to {output_path}")