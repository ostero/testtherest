#!venv3/bin/python3

import requests
import openai
import logging
import json
import ast
import numexpr
from config import Config

SYSTEM_PROMPT = (
    "You are a helpful assistant. You speak Polish fluently. "
    "You are given a few sentences in Polish. "
    "The sentences contain personal information. "
    "Your task is to censor this information. "
    "Find the person's name and surname and replace it with the single word 'CENZURA'. "
    "Find the address data. Replace the city name with the single word 'CENZURA'. "
    "Next find the street name and the house number, and join them to a single string. "
    "Next replace this string with the single word 'CENZURA'. "
    "Leave the words like 'ulica', 'ul.', 'aleja', 'al.', 'osiedle', 'os.', etc. where they are. Do not replace them. "
    "Next find the age of the person. Replace only the number representing the person's age with the word 'CENZURA'. "
    "Keep the oryginal punctuation and formatting. "
    "Do not add any additional information. "
    "Do not add line breaks. " 
)
OUTPUT_FILE = "input_data.txt"

CONTENT_TYPE_HEADER = {'Content-Type': 'application/json;charset=UTF-8'}

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def retrieve_data(url: str) -> str | None:
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        logging.error(f"Error fetching question: {e}")
        return None

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
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        logging.error(f"Error communicating with robot: {e}")
        return None

def get_llm_answer(
    question: str, apikey: str, system_prompt: str = SYSTEM_PROMPT
) -> str | None:
    """Get an answer from OpenAI LLM for the given question."""
    try:
        openai.api_key = apikey
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error getting LLM answer: {e}")
        return None

def main() -> None:
    try:
        config = Config.load_from_yaml()
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        return

    if not config.is_valid():
        logging.error("Invalid configuration.")
        return

    data = retrieve_data(config.src.replace("YOUR-KEY", config.apikey))
    if data is None:
        logging.error("No data retrieved.")
        return

    save_data(data, OUTPUT_FILE)

    # Example: Evaluate math expressions in test-data
    censored_data = get_llm_answer(data, config.llmkey)                
    logging.debug(f"Test data: {data}")
    logging.debug(f"Test censored data: {censored_data}")

    verification_request = dict()
    verification_request["task"] = "CENZURA"
    verification_request["apikey"] = config.apikey
    verification_request["answer"] = censored_data.replace("CENZURA CENZURA", "CENZURA") 

    verification_response = talk_to_robot(config.dest, verification_request)
    
    if verification_response is None:
        logging.error("Failed to send response.")
        return

    logging.info(f"Robot answers: {verification_response}")

if __name__ == "__main__":
    main()
