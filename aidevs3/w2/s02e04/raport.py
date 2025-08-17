import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

org_files = 'pliki_z_fabryki'
decoded_files = 'decoded_pliki_z_fabryki'
files_to_classify = 'files_to_classify'

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

def append_file(tag: str, text: str) -> None:
    with open("raports.txt", "a+", encoding="utf-8") as raports_file:
        raports_file.write(f"FILE: {tag}\n")
        raports_file.write(text + "\n\n")

def main() -> None:
    # Load the model (choose a size)
    
    for filename in os.listdir(org_files):
        if filename.lower().endswith('.txt'):
            filenameWithoutExtension = os.path.splitext(filename)[0]
            filepath = os.path.join(org_files, filename)
            logging.info(filenameWithoutExtension);
            raport = read_data(filepath)
            logging.info(raport)
            save_data(raport, os.path.join(files_to_classify, filenameWithoutExtension + ".txt"))
        if filename.lower().endswith('.png'):
            filenameWithoutExtension = os.path.splitext(filename)[0]
            filepath = os.path.join(decoded_files, filenameWithoutExtension) + ".txt"
            logging.info(filenameWithoutExtension);
            raport = read_data(filepath)
            logging.info(raport)
            save_data(raport, os.path.join(files_to_classify, filenameWithoutExtension + ".png"))
        if filename.lower().endswith('.mp3'):
            filenameWithoutExtension = os.path.splitext(filename)[0]
            filepath = os.path.join(decoded_files, filenameWithoutExtension) + ".txt"
            logging.info(filenameWithoutExtension);
            raport = read_data(filepath)
            logging.info(raport)
            save_data(raport, os.path.join(files_to_classify, filenameWithoutExtension + ".mp3"))

if __name__ == "__main__":
    main()

