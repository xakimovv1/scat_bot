# ocr/parser.py
import easyocr
import re

reader = easyocr.Reader(['en', 'ru'])

def extract_payment_data(image_path):
    result = reader.readtext(image_path, detail=0)
    text = " ".join(result).lower()

    text = text.replace(",", "").replace("сўм", "so'm").replace("сум", "so'm").replace("uzs", "so'm")

    # 1. To‘lov summasini aniqlash
    summa = None

    # Uslublar:
    patterns = [
        r'(\d{1,3}(?:[\s.]\d{3})+)\s*so[\'’`‘’ʻ’ʼʼm]',  # 12 000 so‘m
        r'(\d{4,6})\s*so[\'’`‘’ʻ’ʼʼm]',                 # 12000 so‘m
        r'summa[:\-]?\s*(\d{4,6})',                     # summa: 12000
        r'oplacheno[:\-]?\s*(\d{4,6})',                 # oplacheno: 12000
        r'итого[:\-]?\s*(\d{4,6})',                     # итого: 12000
        r'(\d{4,6})\s*(?:rub|so[\'’`‘’ʻ’ʼʼm])?'         # 12000 (yakka raqam)
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            summa = match.group(1).replace(" ", "").replace(".", "")
            break

    # 2. Karta raqami — oxirgi 4 ta raqam
    card_match = re.findall(r'\b\d{4}\b', text)
    card = card_match[-1] if card_match else "0000"

    return {
        "summa": summa or "❌",
        "card": card,
        "raw_text": text
    }

# Test qilish
if __name__ == "__main__":
    print(extract_payment_data("test.jpg"))
