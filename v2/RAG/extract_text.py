from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a given PDF file.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        str: Extracted text from the PDF.
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

if __name__ == "__main__":
    pdf_path = input("Enter the path to the PDF file: ")
    extracted_text = extract_text_from_pdf(pdf_path)
    with open("Datasets/extracted_text.txt", "w", encoding="utf-8") as file:
        file.write(extracted_text)
    print("Text extracted and saved to 'extracted_text.txt'")


# v2/Datasets/Grade-04-English-textbook-English-Medium-–-New-Syllabus.pdf