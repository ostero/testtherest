#!venv3/bin/python3

import openai
import base64
import logging
import requests
import os
import re
import json
import time
from config import Config
import wget
import time

CONTENT_TYPE_HEADER = {'Content-Type': 'application/json;charset=UTF-8'}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

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

def talk_to_robot(url: str, data: dict) -> dict | None:
    """Send a POST request with JSON data and return the response as a dict."""
    try:
        response = requests.post(url, json=data, headers=CONTENT_TYPE_HEADER)
        logging.info(response)
        logging.info(response.text)
        save_data(response.text, "robot_response.txt")
        response.raise_for_status()
        return response.text
    except (requests.RequestException, ValueError) as e:
        logging.error(f"Error communicating with robot: {e}")
        return None

def get_image_names(command: str) -> list[str]:
    verification_request = dict()
    verification_request["task"] = "photos"
    verification_request["apikey"] = config.apikey
    verification_request["answer"] = command

    verification_response = talk_to_robot(config.dest, verification_request)
    if verification_response is None:
        logging.error("Failed to get images from robot.")
        return
    return re.findall("IMG.[^\.]*\.PNG", verification_response)

def download_images(image_names: list[str]) -> None:
    """Download images from the robot's response."""
    image_url = "https://centrala.ag3nts.org/dane/barbara/"
    for image in image_names:
        logging.info(f"Downloading image: {image_url}{image}")
        wget.download(image_url + image, out="images" )
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def ask_openai(system_prompt: str, user_prompt) -> str | None:
    global config
    try:        
        openai.api_key = config.llmkey
        response = openai.responses.create(
            model = config.openai_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.output_text.strip()
    except Exception as e:
        logging.error(f"Error getting LLM answer: {e}")
        return None

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

    good_image_names = []
    image_names = get_image_names("START")
    logging.info(f"Robot answers: {image_names}")
    download_images(image_names)
    while len(image_names) > 0:
        logging.info(f"Remaining images to process: {len(image_names)}")
        for image_name in image_names:
            image_path = os.path.join("images", image_name)
  
            encoded_image = encode_image(image_path)
            
            answer = ask_openai(
            (
                "Proszę o pomoc w analizie zdjęcia.\n"
                "Potrzebuję ryspisu kobiety, która jest na zdjęciu.\n"
                "Uwaga, zdjęcie może być uszkodzone.\n"
                "Przeanalizuj jakość tego zdjęcia.\n"
                "Jeśli na zdjęciu jest kobieta i można ją rozpoznać, odpowiedz OK.\n"
                "Jeśli zdjęcie jest uszkodzone lub zaszumione odpowiedz REPAIR.\n"
                "Jeśli zdjęcie jest za ciemne odpowiedz BRIGHTEN.\n"
                "Jeśli zdjęcie jest za jasne odpowiedz DARKEN.\n"
                "Jeśli zdjęcie jest dobrej jakości lecz nie przedstawia kobiety, odpowiedz BAD.\n"
                "Proszę odpowiedzieć tylko jednym słowem, bez dodatkowego tekstu.\n"
            ),
            [
                {"type": "input_text", "text": "Przeanalizuj zdjęcie: " + image_name},
                {"type": "input_image", "image_url": f"data:image/png;base64,{encode_image('images/' + image_name)}"}
            ]
            )
            image_names.remove(image_name)
            if answer:
                logging.info(f"LLM response for {image_name}: {answer}")
                if answer == "OK":
                    logging.info(f"Image {image_name} is good.")
                    good_image_names.append(image_name)
                elif answer == "REPAIR" or answer == "DARKEN" or answer == "BRIGHTEN":
                    logging.info(f"Image {image_name} needs repair.")
                    repaired_image_names = get_image_names(answer + " " + image_name)
                    download_images(repaired_image_names)
                    image_names.extend(repaired_image_names)
                elif answer == "BAD":
                    logging.info(f"Image {image_name} does not contain a woman.")
            else:
                logging.error(f"Failed to get LLM response for {image_name}.")
            time.sleep(5)  # To avoid hitting API rate limits
    if len(good_image_names) > 0:
        logging.info(f"Good images: {good_image_names}")
        user_prompt = []
        for image_name in good_image_names:
            user_prompt.append({"type": "input_text", "text": "Zdjęcie: " + image_name})
            user_prompt.append({"type": "input_image", "image_url": f"data:image/png;base64,{encode_image('images/' + image_name)}"})
        answer = ask_openai(
        (
                "Otrzymasz kilka zdjęć kobiety. Kobieta ta ma na imię Barbara.\n"
                "Proszę podaj rysopis Barbary w języku polskim.\n"
                "Uwaga, na niektórych zdjęcich mogą występować też inne osoby.\n"
                "Barbara to ta kobieta, która występuje na większości zdjęć.\n"
                "Proszę zwróć uwagę na wszystkie szczegóły, które mogą być istotne.\n"
                "Podaj szczegółowy rysopis, który pomoże w jej odnalezieniu.\n"
        ), user_prompt)
        if answer:
            logging.info(f"LLM response: {answer}")
            save_data(answer, "answer.txt")
            verification_request = dict()
            verification_request["task"] = "photos"
            verification_request["apikey"] = config.apikey
            verification_request["answer"] = answer
        
            verification_response = talk_to_robot(config.dest, verification_request)
            if verification_response is None:
                logging.error("Failed to get images from robot.")
                return
            logging.info(f"Robot answers: {verification_response}")
            
        
    else:
        logging.info("No good images found.")   


if __name__ == "__main__":
    main()
