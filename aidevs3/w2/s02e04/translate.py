#!venv3/bin/python3

import ollama
import os
import logging
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

directory = 'pliki_z_fabryki'

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

    for filename in os.listdir(directory):
        if filename.lower().endswith('.mp3'):
            filepath = os.path.join(directory, filename)
            filenameWithoutExtension = os.path.splitext(filename)[0]
            logging.info(filenameWithoutExtension);
            transcriptions = read_data(os.path.join(directory, filenameWithoutExtension + ".txt"))
            logging.info(transcriptions )
            translation_pl = ask_ollama( (
                    "Otrzymasz tekst w języku angielskim.\n"
                    "Przetłumacz go na język polski.\n"
                    "Odpowiedz zwięźle, bez zbędnych komentarzy. Tylko przetłumaczony tekst.\n"
                ), (
                    f"{transcriptions}"
                ))
            logging.info(translation_pl)
            save_data(translation_pl, os.path.join(directory, filenameWithoutExtension + ".pl.txt"))

if __name__ == "__main__":
    main()
