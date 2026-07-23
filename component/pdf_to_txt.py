import re
import pdfplumber



def unwrap_broken_lines(text: str) -> str:
    text = re.sub(r"(?<![\.\:\n])\n(?!\n)", " ", text)
    return re.sub(r" +", " ", text)


def clean_extracted_text(text: str) -> str:
    text = re.sub(
        r"\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*(?:AM|PM).*?https?://\S+",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(r"\b\d+/\d+\b", "", text)

    text = re.sub(r" pointson ", " points on ", text, flags=re.IGNORECASE)
    text = re.sub(r"beneﬁt", "benefit", text, flags=re.IGNORECASE)
    text = re.sub(r"Oﬀer", "Offer", text, flags=re.IGNORECASE)

    text = re.sub(r"[^\w\s\$\%\,\.\-\:\/\(\)\–\—\*\&\#\']", " ", text)

    text = unwrap_broken_lines(text)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def pdf_to_clean_txt(file_path: str) -> str:
    raw_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(layout=True)
            if page_text:
                raw_text += page_text + "\n"

    return clean_extracted_text(raw_text)


cleaned_text = pdf_to_clean_txt("./card_details/Chase Sapphire Preferred Credit Card _ Chase.com.pdf")

with open(
    "./card_details/Chase Sapphire Preferred Credit Card _ Chase.com.txt", "w", encoding="utf-8"
) as f:
    f.write(cleaned_text)

print("Text extracted and cleaned successfully!")