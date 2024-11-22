def chunk_text(text, chunk_size=200):
    """
    Splits the text into chunks of specified size.
    Args:
        text (str): The full text to chunk.
        chunk_size (int): Number of words per chunk.
    Returns:
        list: A list of text chunks.
    """
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]


if __name__ == "__main__":
    with open("Datasets/extracted_text.txt", "r", encoding="utf-8") as file:
        text = file.read()

    chunk_size = int(input("Enter the chunk size (default: 200): ") or 200)
    chunks = chunk_text(text, chunk_size)

    with open("Datasets/chunked_text.json", "w", encoding="utf-8") as file:
        import json

        json.dump(chunks, file, indent=4)
    print("Text chunked and saved to 'chunked_text.json'")
