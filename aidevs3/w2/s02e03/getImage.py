#!venv3/bin/python3

import openai
import logging
import requests
from config import Config

CONTENT_TYPE_HEADER = {'Content-Type': 'application/json;charset=UTF-8'}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_openai_image(user_prompt: str) -> str | None:
    global config
    try:        
        openai.api_key = config.llmkey
        response = openai.images.generate(
        model="dall-e-3",
        prompt= user_prompt,
        size="1024x1024",
        n=1,
        response_format="url" )   
        return response.data[0].url
    except Exception as e:
        logging.error(f"Error getting image from OpenAI: {e}")
        return None


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

def retrieve_description(url: str) -> str | None:
    try:
        resp = requests.get(url, headers={'Content-Type': 'application/json;charset=UTF-8'})
        resp.raise_for_status()
        json_response = resp.json()
        return json_response["description"]
    except requests.RequestException as e:
        logging.error(f"Error fetching robot description: {e}")
        return None
    except ValueError as e:
        logging.error(f"Error decoding JSON: {e}")
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

    description = retrieve_description(config.src.replace("YOUR-KEY", config.apikey))
    if description is None:
        logging.error("No description retrieved.")
        return

    logging.info(description);
    save_data(description, "description.txt")
    image_url = get_openai_image(description)

    logging.info(image_url);
    save_data(image_url, "answer.txt")

    verification_request = dict()
    verification_request["task"] = "robotid"
    verification_request["apikey"] = config.apikey
    verification_request["answer"] = image_url

    verification_response = talk_to_robot(config.dest, verification_request)
    
    if verification_response is None:
        logging.error("Failed to send response.")
        return

    logging.info(f"Robot answers: {verification_response}")

if __name__ == "__main__":
    main()
