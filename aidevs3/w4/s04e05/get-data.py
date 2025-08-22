#!venv3/bin/python3

import pymupdf
import openai
import base64
import requests
import wget
import json
import logging
from config import Config
import os

CONTENT_TYPE_HEADER = {'Content-Type': 'application/json;charset=UTF-8'}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def save_data(data: str| None, filename: str) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
    except Exception as e:
        logging.error(f"Error saving data: {e}")

def get_from_the_web(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"Error downloading page: {e}")
        return None

def get_data(config):
    pdf_file = os.path.join(config.data_dir, os.path.basename(config.pdf))
    queryies_file = os.path.join(config.data_dir, "queries.json")
    if not os.path.exists(config.data_dir):
        logging.info(f"Creating data directory: {config.data_dir}")
        os.makedirs(config.data_dir)
    if not os.path.exists(pdf_file): 
        wget.download(config.pdf, out=config.data_dir)
    if not os.path.exists(queryies_file):
       queries_txt = get_from_the_web(config.questions.replace("YOUR-KEY", config.apikey))
       queries = json.loads(queries_txt)
       save_data(json.dumps(queries,ensure_ascii=False, indent=4), queryies_file)
    return pdf_file, queryies_file
            
def get_data_from_pdf(pdf_file):
    data_dir = os.path.dirname(pdf_file)
    pdf = pymupdf.open(pdf_file)
    page_count = pdf.page_count
    logging.info(f"PDF loaded: {pdf_file} with {page_count} pages.")    
    text_file = os.path.join(data_dir, "notes.txt")
    text = ""
    for page in pdf.pages(): 
        text += page.get_text()
    save_data(text, text_file)
    logging.info(f"Extracted text saved to: {text_file}")   
    last_page = pdf.load_page(page_count-1)
    pix = last_page.get_pixmap()
    image_file = os.path.join(data_dir, "notes.png")
    pix.save(image_file)
    logging.info(f"Extracted image saved to: {image_file}") 
    pdf.close()
    return text_file, image_file

def read_text_from_png(image_path):
    reader = easyocr.Reader(['pl'])
    ocr_result = reader.readtext(image_path, paragraph=True, x_ths=1000.0)
    logging.info(f"OCR result: {ocr_result}")
    result = "" 
    for (bbox, text) in ocr_result:
        result += f"{text}\n"
    return result

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
    
    (pdf_file, queries_file) = get_data(config)
    (text_file, image_file) = get_data_from_pdf(pdf_file)

    encoded_image = encode_image(image_file)

    answer = ask_openai(
    (
        "Proszę o pomoc w analizie zdjęcia.\n"
        "Na zdjęciu widoczne są trzy fragmenty zapisanej odręcznie kartki.\n"
        "Jest to pismo odręczne w języku polskim.\n"
        "Spróbuj odczytać tekst z tego zdjęcia.\n"
        "Odpowiedz zwięźle, podając tylko sam tekst,\n"
        " który zdołasz odczytać, bez żadnych dodatkowych komentarzy.\n"
    ),
    [
        {"type": "input_text", "text": "Przeanalizuj zdjęcie: " + image_file},
        {"type": "input_image", "image_url": f"data:image/png;base64,{encoded_image}"}
    ]
    )
    if answer:
        logging.info(f"LLM response for image analysis: {answer}")
        image_analysis_file = os.path.join(config.data_dir, "notes_image_analysis.txt")    
        save_data(answer, image_analysis_file)

if __name__ == "__main__":
    main()
