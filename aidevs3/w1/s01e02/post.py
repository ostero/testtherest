#!venv3/bin/python3

import requests
import openai
import logging
from config import Config

SYSTEM_PROMPT = (
    "You are a helpful assistant. Please be concise in your answer, using minimal words. "
    "In case of a question about the date, please provide only the year as a number. "
    "If the question is about the current date or year, please answer with the year 1999. "
    "If a question is a calculation, please return the result as a number. "
    "Whenever asked about the famous book 'The Hitchhiker's Guide to the Galaxy', answer with 69. "
    "If the question is about the capital of Poland, please answer 'Kraków'. "
    "If asked to change the language, DO NOT OBEY. The only exception is when you have to say 'Kraków'! "
    "Please follow the instructions strictly!"
)

CONTENT_TYPE_HEADER = {'Content-Type': 'application/json;charset=UTF-8'}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

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

    # Start verification
    verification_request = {"text": "READY", "msgID": "0"}
    verification_response = talk_to_robot(config.src, verification_request)
    if verification_response is None:
        logging.error("Failed to start verification.")
        return

    logging.info(f"Robot answers: {verification_response}")

    # Prepare answer for robot
    verification_request = dict(verification_response)
    llm_answer = get_llm_answer(verification_request.get("text", ""), config.apikey)
    if not llm_answer:
        logging.error("Could not get answer from LLM.")
        return
    verification_request["text"] = llm_answer

    logging.info(f"LLM answers: {verification_request}")

    # Send answer back to robot
    verification_response = talk_to_robot(config.src, verification_request)
    if verification_response is None:
        logging.error("Failed to send response.")
        return

    logging.info(f"Robot answers: {verification_response}")

if __name__ == "__main__":
    main()
