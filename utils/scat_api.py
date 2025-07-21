# utils/scat_api.py
import requests

def check_pay(account: str, txn_id: str, summa: str):
    url = "http://746c.cloudtaxi.ru/money/check_pay/"
    params = {
        "command": "check",
        "txn_id": txn_id,
        "account": account,
        "sum": summa
    }
    try:
        response = requests.get(url, params=params)
        return response.status_code, response.text
    except Exception as e:
        return 500, str(e)

def do_pay(account: str, txn_id: str, summa: str):
    url = "http://746c.cloudtaxi.ru/money/check_pay/"
    params = {
        "command": "pay",
        "txn_id": txn_id,
        "account": account,
        "sum": summa
    }
    try:
        response = requests.get(url, params=params)
        return response.status_code, response.text
    except Exception as e:
        return 500, str(e)

# Test qilish uchun
if __name__ == "__main__":
    code, resp = check_pay("P2", "20250718123059", "15000")
    print("CHECK:", code, resp)

    code, resp = do_pay("P2", "20250718123059", "15000")
    print("PAY:", code, resp)
