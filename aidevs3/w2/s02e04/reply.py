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

CONTENT_TYPE_HEADER = {'Content-Type': 'application/json;charset=utf-8'}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

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

    with open('answer.json') as f:
        answer = json.load(f)

    verification_request = dict()
    verification_request["task"] = "kategorie"
    verification_request["apikey"] = config.apikey
    verification_request["answer"] = answer

    logging.info(json.dumps(verification_request, indent=4))

    verification_response = talk_to_robot(config.dest, verification_request)
    
    if verification_response is None:
        logging.error("Failed to send response.")
        return

    logging.info(f"Robot answers: {verification_response}")

if __name__ == "__main__":
    main()
