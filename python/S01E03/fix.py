#!venv3/bin/python3

import requests
import openai
import logging
import json
import ast
import numexpr
from config import Config

SYSTEM_PROMPT = (
    "You are a helpful assistant. Please be concise in your answer, using minimal words. "
    "If possible answer with a single word. "
)
OUTPUT_FILE = "input_data.txt"

CONTENT_TYPE_HEADER = {'Content-Type': 'application/json;charset=UTF-8'}

logging.basicConfig(
    level=logging.INFO,
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

    # Verify if data is valid JSON
    try:
        json_data = json.loads(data)
        logging.info("Data is valid JSON.")
    except json.JSONDecodeError as e:
        logging.error(f"Data is not valid JSON: {e}")
        return

    # Example: Evaluate math expressions in test-data
    if "test-data" in json_data:
        for test_data in json_data["test-data"]:
            if isinstance(test_data, dict):
                question = test_data.get("question")
                if question:
                    try:
                        # Evaluate the math expression safely using numexpr
                        result = numexpr.evaluate(question).item()
                        logging.debug(f"Evaluated '{question}' = {result}")
                    except Exception as e:
                        logging.error(f"Error evaluating expression '{question}': {e}")
                answer = test_data.get("answer")
                if answer:
                    if result == answer:
                        logging.debug(f"Answer '{answer}' is correct.")
                    else:
                        logging.error(f"Evaluated '{question}' = {result}")
                        logging.error(f"Answer '{answer}' is incorrect. Expected: {result}")
                        test_data["answer"] = result
                else:
                    logging.error("No answer provided for the question.")
                    test_data["answer"] = result
                test = test_data.get("test")
                if test:
                    if isinstance(test, dict) and "q" in test:
                        question = test.get("q") 
                        answer = get_llm_answer(question, config.llmkey)                
                        test["a"] = answer
                        logging.debug(f"Test question: {question}")
                        logging.debug(f"Test answer: {answer}")

    json_data["apikey"] = config.apikey

    verification_request = dict()
    verification_request["task"] = "JSON"
    verification_request["apikey"] = config.apikey
    verification_request["answer"] = json_data

    verification_response = talk_to_robot(config.dest, verification_request)
    
    if verification_response is None:
        logging.error("Failed to send response.")
        return

    logging.info(f"Robot answers: {verification_response}")

if __name__ == "__main__":
    main()
