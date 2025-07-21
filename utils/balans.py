# utils/balans.py
import os, json

BALANS_FILE = "balans.json"
FINE_AMOUNT = 5000  # jarima summasi (o‘zgartirsa bo‘ladi)

def load_balans():
    if not os.path.exists(BALANS_FILE):
        return {}
    with open(BALANS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_balans(data):
    with open(BALANS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def approve_payment(pozivnoy, amount):
    data = load_balans()
    data[pozivnoy] = data.get(pozivnoy, 0) + amount
    save_balans(data)

def apply_fine(pozivnoy, entered_amount, detected_amount):
    data = load_balans()
    if entered_amount > detected_amount:
        fine = FINE_AMOUNT
    else:
        fine = 0
    data[pozivnoy] = data.get(pozivnoy, 0) - fine
    save_balans(data)
