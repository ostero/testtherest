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
import zipfile

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

    good_data = []
    with open(config.data_dir + "/verify.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            (line_no, data) = line.split("=")
            logging.info(f"Processing line {line_no}: {data}")
            answer = ask_openai("validate data", data)
            if answer == "1":
                logging.info(f"Line {line_no} is correct.")
                good_data.append(line_no)
            time.sleep(1)
                
    logging.info(f"Good data: {good_data}")
    verification_request = dict()
    verification_request["task"] = "research"
    verification_request["apikey"] = config.apikey
    verification_request["answer"] = good_data
   # json.dumps(good_data,separators=(',\n', ':') )
    save_data(json.dumps(verification_request,indent=4), "answer.json")

    verification_response = talk_to_robot(config.dest, verification_request)
    if verification_response is None:
        logging.error("Failed to send response.")
        return

    logging.info(f"Robot answers: {verification_response}")

if __name__ == "__main__":
    main()
