import easyocr
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

src_directory = 'pliki_z_fabryki'
dst_directory = 'decoded_pliki_z_fabryki'

def read_text_from_png(image_path):
    reader = easyocr.Reader(['en', 'pl'])
    ocr_result = reader.readtext(image_path, paragraph=True, x_ths=1000.0)
    logging.info(f"OCR result: {ocr_result}")
    result = "" 
    for (bbox, text) in ocr_result:
        result += f"{text}\n"
    return result

def save_data(data: str| None, filename: str) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
    except Exception as e:
        logging.error(f"Error saving data: {e}")

def main() -> None:
    # Load the model (choose a size)
    
    for filename in os.listdir(src_directory):
        if filename.lower().endswith('.png'):
            filepath = os.path.join(src_directory, filename)
            filenameWithoutExtension = os.path.splitext(filename)[0]
            logging.info(filenameWithoutExtension);
            result = read_text_from_png(filepath)
            logging.info(result)
            save_data(result, os.path.join(dst_directory, filenameWithoutExtension + ".txt"))

if __name__ == "__main__":
    main()

