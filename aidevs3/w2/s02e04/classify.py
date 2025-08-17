#!venv3/bin/python3

import ollama
import openai
import logging
import requests
import os
import json
import time
from config import Config

files_to_classify = 'files_to_classify'

CONTENT_TYPE_HEADER = {'Content-Type': 'application/json;charset=UTF-8'}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

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
def classify_file(filepath: str) -> str|None:
    note = read_data(filepath)
    return ask_openai((
        "You are a helpful assistant.\n"
        "You will be given a note.\n"
        "Please cattegorize the note into one of the following categories:\n"
        "Does the note contain information about:\n"
        "1. People: Include only notes containing information about captured people or traces of their presence."
        "2. Hardware: Include only notes containing information about repaired hardware faults.\n"
        "3. Other.\n"
        "Be carefull.\n"
        "Mind that software updates are not hardware faults.\n"
        "When the note states that no one was foud, please assign it to the \"Other\" category.\n"
        "Please be concise and return only the category name.\n"
        ),(
        f"{note}\n"
        ))

def talk_to_robot(url: str, data: dict) -> dict | None:
    """Send a POST request with JSON data and return the response as a dict."""
    try:
        response = requests.post(url, json=data, headers=CONTENT_TYPE_HEADER)
        logging.info(response)
        logging.info(response.text)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        logging.error(f"Error communicating with robot: {e}")
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

    people = []
    hardware = []
    for filename in os.listdir(files_to_classify):
        filepath = os.path.join(files_to_classify, filename)
        classification = classify_file(filepath)
        logging.info(f"{filename}: {classification}");
        if "People" in classification.title():
            people.append(filename)
        elif "Hardware" in classification.title():
            hardware.append(filename)
        time.sleep(5)  # To avoid hitting API rate limits

    verification_request = dict()
    verification_request["task"] = "kategorie"
    verification_request["apikey"] = config.apikey
    verification_request["answer"] = {
        "people": people,
        "hardware": hardware
    } 
    save_data(json.dumps(verification_request["answer"], indent=4), "answer.json")

    verification_response = talk_to_robot(config.dest, verification_request)
    
    if verification_response is None:
        logging.error("Failed to send response.")
        return

    logging.info(f"Robot answers: {verification_response}")

if __name__ == "__main__":
    main()
