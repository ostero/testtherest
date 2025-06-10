#!venv3/bin/python3

import ollama
import openai
import logging
import requests
from config import Config

CONTENT_TYPE_HEADER = {'Content-Type': 'application/json;charset=UTF-8'}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def ask_ollama(system_prompt: str, user_prompt: str) -> str | None:
    global config
    response = ollama.chat(
        model = config.ollama_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response['message']['content']

def ask_openai(system_prompt: str, user_prompt: str) -> str | None:
    global config
    try:        
        openai.api_key = config.llmkey
        response = openai.chat.completions.create(
            model = config.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error getting LLM answer: {e}")
        return None

def talk_to_robot(url: str, data: dict) -> dict | None:
    """Send a POST request with JSON data and return the response as a dict."""
    try:
        response = requests.post(url, json=data, headers=CONTENT_TYPE_HEADER)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        logging.error(f"Error communicating with robot: {e}")
        return None

def read_data(filename: str) -> str| None:
    data = None
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read()
    return data

def save_data(data: str| None, filename: str) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
    except Exception as e:
        logging.error(f"Error saving data: {e}")


def main() -> None:
    global config
    try:
        config = Config.load_from_yaml()
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        return

    if not config.is_valid():
        logging.error("Invalid configuration.")
        return

    transcriptions = read_data("transcription.txt")

    workplaces = ask_ollama( (
            "Otrzymasz transkrypcję wypowiedzi kilku osób.\n"
            "Przeanalizuj je uważnie.\n"
            "Znajdź informacje o pewnym profesorze, który nazywa się Andrzej Maj.\n"
            "Informacje o Andrzeju Maju zaczerpnij wyłącznie z przytoczonych transkrypcji, "
            "aby nie mylić go z innymi osobami o tym samym nazwisku!\n"
            "Zwróć szczególnie uwagę na to gdzie pracował i prowadził wykłady Andrzej Maj.\n"
            "Oto transkrypcje nagrań kilku osób (mogą zawierać błędy lub być chaotyczne, niektóre mogą wprowadzać w błąd):\n"
            f"{transcriptions}\n\n"
            "Jeśli będziesz zapytany o miejsca wykładów profesora Andrzeja Maja, to\n" 
            "dla każdego z nich podaj nazwę jednoskti, nazwę uczelni lub instytucji i miasto, w którym ta jednostka się znajduje.\n"
            "Odpowiedz zwięźle, bez zbędnych komentarzy.\n"
            "Jedna linia to jedno miejsce.\n"
            "Przykład:\n"
            "Instytut Informatyki i Matematyki Komputerowej, Uniwersytet Jagielloński, Kraków\n"
        ), (
            "Podaj miejsca wykładów profesora Andrzeja Maja.\n"
        ))
    logging.info(workplaces)
    save_data(workplaces, "workplaces.txt")

    institutes = ask_ollama((
        "Oto lista miejsc, w których profesor Andrzej Maj prowadził wykłady:\n"
        f"{workplaces}\n\n"
        "Zwróć tylko te, które są instytutami, zachowaj kolejność i format:\n"
        "Nazwa jednostki, nazwa instytucji, miasto\n"
        "Jedna linia to jedno miejsce.\n"
        ),(
        "Które z podanych miejsc, są instytutami?"))

    logging.info(institutes);
    save_data(institutes, "institutes.txt")

    if len(institutes.splitlines()) != 1:
        logging.error("Expected only one line, but got multiple.")
        return

    answer = ask_openai( (
        "Proszę rozmawiajmy po polsku.\n"
        "Jeśli będziesz zapytany o adres jakiegoś instytutu, jednostki, lub wydziału uczelni, podaj adress jednostki a nie siedziby głównej.\n"
        "Pytany o adresy podaj wyłącznie nazwy ulic.\n"
        "Na przyklad: ul. Jana Długosza"),(
        "Podaj adres tego instytutu:\n"
        f"{institutes}\n\n"))

    logging.info(answer);
    save_data(answer, "answer.txt")

    verification_request = dict()
    verification_request["task"] = "mp3"
    verification_request["apikey"] = config.apikey
    verification_request["answer"] = answer

    verification_response = talk_to_robot(config.dest, verification_request)
    
    if verification_response is None:
        logging.error("Failed to send response.")
        return

    logging.info(f"Robot answers: {verification_response}")

if __name__ == "__main__":
    main()
