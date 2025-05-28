#!venv3/bin/python3

import requests
import re
import openai
import logging
from config import Config

OUTPUT_FILE = "output.html"
SYSTEM_PROMPT = (
    "You are a helpful assistant. Please be concise in your answer "
    "using minimal words. In case of a question about the date, "
    "please provide only the year as a number."
)
CONTENT_TYPE_HEADER = {'Content-Type': 'application/x-www-form-urlencoded'}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def fetch_question(url: str) -> str | None:
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        match = re.search(
            r'id="human-question">.*?<br\s*/?>([^<]*)<', resp.text, re.DOTALL
        )
        if match:
            return match.group(1).strip()
        return None
    except requests.RequestException as e:
        logging.error(f"Error fetching question: {e}")
        return None

def get_llm_answer(
    question: str, apikey: str, system_prompt: str = SYSTEM_PROMPT
) -> str | None:
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

def post_answer(
    url: str, username: str, password: str, answer: str
) -> requests.Response | None:
    try:
        data = {'username': username, 'password': password, 'answer': answer}
        return requests.post(url, data=data, headers=CONTENT_TYPE_HEADER)
    except requests.RequestException as e:
        logging.error(f"Error posting answer: {e}")
        return None

def save_html_response(response: requests.Response | None, filename: str) -> None:
    if response is None:
        logging.warning("No response to save.")
        return
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
    except Exception as e:
        logging.error(f"Error saving HTML response: {e}")

def main() -> None:
    try:
        config = Config.load_from_yaml()
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        return

    if not config.is_valid():
        logging.error("Invalid configuration.")
        return

    question = fetch_question(config.src)
    if not question:
        logging.error("Could not extract the question text.")
        return

    answer = get_llm_answer(question, config.apikey)
    if not answer:
        logging.error("Could not get answer from LLM.")
        return

    logging.info(f"Question: {question}")
    logging.info(f"LLM answer: {answer}")

    response = post_answer(
        config.dest, config.auth['username'], config.auth['password'], answer
    )
    if response is None:
        logging.error("Failed to post answer.")
        return

    logging.info(f"POST status: {response.status_code}")
    save_html_response(response, OUTPUT_FILE)

if __name__ == "__main__":
    main()
