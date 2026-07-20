from PyPDF2 import PdfReader

def pdf_to_txt(file_path):
    with open(file_path, "rb") as file: 
        read_file = PdfReader(file)
        text = ""
        for page in read_file.pages: 
            text += page.extract_text()
        
        return text

text = pdf_to_txt("./card_details/Pricing and Terms.pdf")

def save_text_in_txt(): 
    output_path = "./card_details/Terms.txt"
    with open(output_path, "w", encoding="utf-8") as text_file: 
        text_file.write(text)

saved_path = save_text_in_txt()
print(f"Text successfully saved to {saved_path}")