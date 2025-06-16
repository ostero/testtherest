#!venv3/bin/python3

import base64
import openai
import logging
import requests
from config import Config

CONTENT_TYPE_HEADER = {'Content-Type': 'application/json;charset=UTF-8'}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

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

    answer = ask_openai(
        (
            "You are a helpful assistant who can read text from images and maps.\n"
            "You will be given images, four fragments of maps of polish cities.\n"
            "Please analyze all of them.\n"
            "Read the maps and try to figure out the city they represent.\n"
            "Be carefull, one fragment belongs to a different city.\n"
            "Find out the city name that is common to three of the maps.\n"
            "Please answer with the name of the city only, without any additional text.\n"
        ),
        [
            {"type": "input_text", "text": "what's the common name of the city presented on three of the attached maps?"},
            {"type": "input_image", "image_url": f"data:image/png;base64,{encode_image('maps/map4.png')}"},
            {"type": "input_image", "image_url": f"data:image/png;base64,{encode_image('maps/map3.png')}"},
            {"type": "input_image", "image_url": f"data:image/png;base64,{encode_image('maps/map2.png')}"},
            {"type": "input_image", "image_url": f"data:image/png;base64,{encode_image('maps/map1.png')}"}
        ]
    )

    logging.info(answer);
    save_data(answer, "answer.txt")

if __name__ == "__main__":
    main()
