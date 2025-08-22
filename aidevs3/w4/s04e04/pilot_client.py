import requests
import json
from config import Config

def send_instruction(instruction, url="http://localhost:8080/pilot"):
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {"instruction": instruction}
    response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False))
    try:
        print("Status:", response.status_code)
        print("Odpowiedź serwera:", response.json())
    except Exception:
        print("Status:", response.status_code)
        print("Odpowiedź serwera (nie JSON):", response.text)

if __name__ == "__main__":
    config = Config.load_from_yaml()
    if not config.is_valid():
        logging.error("Invalid configuration. HTTP server will not start.")
    instrukcja = input("Podaj instrukcję lotu drona: ")

    send_instruction(instrukcja, f"http://localhost:{config.port}/pilot")